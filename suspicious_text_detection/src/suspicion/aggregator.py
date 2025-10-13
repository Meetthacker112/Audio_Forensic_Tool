from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime, timezone

from .segmenter import SentenceSegmenter, detect_language
from .keywords import KeywordStore, KeywordHit
from .zero_shot import ZeroShotClassifier
from .openai_client import OpenAIAnalyzer
from .config import load_config


@dataclass(frozen=True)
class DetectionResult:
    sentence: str
    language: str
    detected_by: List[str]
    flags: List[str]
    labels: List[Dict[str, float]]
    confidence: float
    explanation: str
    translation: Optional[str]
    sources: Dict[str, Optional[float]]
    timestamp: str


class SuspicionAnalyzer:
    """Hybrid analyzer that combines keywords, zero-shot, and optional OpenAI."""

    def __init__(self) -> None:
        self.cfg = load_config()
        self.logger = logging.getLogger(__name__)
        self.segmenter = SentenceSegmenter()
        self.keywords = KeywordStore(self.cfg.keywords_path)
        self.zero_shot = ZeroShotClassifier()
        self.openai = OpenAIAnalyzer()

    def _score_from_sources(self, kw_hits: List[KeywordHit], zs_scores: Dict[str, float], openai_conf: Optional[float]) -> float:
        score = 0.0
        if kw_hits:
            # Critical > High > Medium > Low
            severities = [h.severity for h in kw_hits]
            if any(s == "CRITICAL" for s in severities):
                score += 0.6
            elif any(s == "HIGH" for s in severities):
                score += 0.45
            elif any(s == "MEDIUM" for s in severities):
                score += 0.3
            else:
                score += 0.15
        if zs_scores:
            score += min(max(max(zs_scores.values()), 0.0), 1.0) * 0.35
        if openai_conf is not None:
            score += min(max(openai_conf, 0.0), 1.0) * 0.4
        return max(0.0, min(score, 1.0))

    def _explain(self, kw_hits: List[KeywordHit], zs_scores: Dict[str, float], openai_flags: Optional[List[str]]) -> str:
        reasons: List[str] = []
        if kw_hits:
            reasons.append(f"Keyword match: {', '.join(sorted({h.keyword for h in kw_hits}))}")
        if zs_scores:
            top = sorted(zs_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            reasons.append("Zero-shot labels: " + ", ".join(f"{k}={v:.2f}" for k, v in top))
        if openai_flags:
            reasons.append("OpenAI flags: " + ", ".join(openai_flags))
        return "; ".join(reasons) if reasons else "No indicators"

    async def analyze_sentence(self, sentence: str, language: Optional[str] = None) -> Optional[DetectionResult]:
        lang = (language or detect_language(sentence)).lower()
        kw_hits = self.keywords.find_flags(sentence, language=lang)
        zs_scores = self.zero_shot.classify(sentence)

        openai_data = None
        if self.openai.enabled:
            openai_data = await self.openai.analyze_sentence(sentence, language=lang)

        openai_conf = float(openai_data.get("confidence", 0.0)) if isinstance(openai_data, dict) else None
        openai_flags = openai_data.get("flags") if isinstance(openai_data, dict) else None

        detected_by: List[str] = []
        if kw_hits:
            detected_by.append("keywords")
        if zs_scores and max(zs_scores.values()) >= 0.5:
            detected_by.append("zero_shot")
        if openai_conf and openai_conf >= 0.6:
            detected_by.append("openai")

        flags = sorted({h.keyword for h in kw_hits})
        if isinstance(openai_flags, list):
            flags = sorted(set(flags) | {str(x) for x in openai_flags})

        labels = []
        if zs_scores:
            labels = [{"label": k, "score": float(v)} for k, v in sorted(zs_scores.items(), key=lambda x: x[1], reverse=True)[:3]]

        confidence = self._score_from_sources(kw_hits, zs_scores, openai_conf)
        explanation = self._explain(kw_hits, zs_scores, openai_flags if isinstance(openai_flags, list) else None)

        if not detected_by:
            # No sufficient signal
            return None

        return DetectionResult(
            sentence=sentence,
            language=lang,
            detected_by=detected_by,
            flags=flags,
            labels=labels,
            confidence=confidence,
            explanation=explanation,
            translation=None,
            sources={
                "keywords": 1.0 if kw_hits else None,
                "zero_shot": max(zs_scores.values()) if zs_scores else None,
                "openai": openai_conf,
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    async def analyze_text(self, text: str, language: Optional[str] = None) -> List[DetectionResult]:
        if not text or not text.strip():
            return []
        lang = (language or detect_language(text)).lower()
        sentences = self.segmenter.segment(text, language=lang)
        tasks = [self.analyze_sentence(sent, language=lang) for sent in sentences]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    def analyze_text_sync(self, text: str, language: Optional[str] = None) -> List[DetectionResult]:
        try:
            return asyncio.run(self.analyze_text(text, language=language))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.analyze_text(text, language=language))
