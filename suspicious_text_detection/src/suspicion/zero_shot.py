from __future__ import annotations

from typing import Dict, List, Optional
from functools import lru_cache

from .config import load_config

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None  # type: ignore


class ZeroShotClassifier:
    """Zero-shot classifier wrapper with lazy initialization.

    Uses English or multilingual models depending on configuration.
    """

    def __init__(self) -> None:
        self.cfg = load_config()
        self._clf = None

    def _ensure_pipeline(self) -> None:
        if self._clf is not None:
            return
        if pipeline is None:
            return
        model_name = self.cfg.zero_shot_model_multi if self.cfg.zero_shot_multilingual else self.cfg.zero_shot_model_en
        try:
            self._clf = pipeline("zero-shot-classification", model=model_name)
        except Exception:
            self._clf = None

    @staticmethod
    def _candidate_labels() -> List[str]:
        # Generic categories that map to keywords
        return [
            "violence",
            "weapons",
            "threats",
            "theft",
            "fraud",
            "smuggling",
            "drugs",
            "kidnapping",
            "general",
            "none",
        ]

    @lru_cache(maxsize=4096)
    def classify(self, sentence: str) -> Dict[str, float]:
        self._ensure_pipeline()
        if self._clf is None:
            return {}
        labels = self._candidate_labels()
        try:
            res = self._clf(sentence, candidate_labels=labels, multi_label=True)
            scores: Dict[str, float] = {}
            for label, score in zip(res["labels"], res["scores"]):  # type: ignore
                scores[str(label)] = float(score)
            return scores
        except Exception:
            return {}
