from __future__ import annotations

from typing import Optional, List, Dict
import json
import logging

from .config import load_config

try:  # pragma: no cover
    from openai import AsyncOpenAI as _AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    _AsyncOpenAI = None  # type: ignore


class OpenAIAnalyzer:
    """Async OpenAI-based semantic analyzer for suspicious content.

    Expects USE_OPENAI=true and OPENAI_API_KEY configured. Returns a compact
    JSON-like dict with is_suspicious, confidence, and flags.
    """

    def __init__(self) -> None:
        self.cfg = load_config()
        self.logger = logging.getLogger(__name__)
        self.enabled = self.cfg.use_openai and (_AsyncOpenAI is not None) and bool(self.cfg.openai_api_key)
        self.model = self.cfg.openai_model
        self._client = None
        if self.enabled and _AsyncOpenAI is not None:
            try:
                self._client = _AsyncOpenAI()
            except Exception as exc:  # pragma: no cover
                self.logger.warning("OpenAI client init failed: %s", exc)
                self._client = None
                self.enabled = False

    async def analyze_sentence(self, sentence: str, language: Optional[str] = None) -> Optional[Dict]:
        if not self.enabled or self._client is None:
            return None
        content = self._build_prompt(sentence, language)
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a forensic text analyst. Given a single sentence, "
                            "decide if it implies criminal, illegal, or suspicious activity. "
                            "Return ONLY a compact JSON object with keys: "
                            "is_suspicious (boolean), confidence (0..1), flags (array of short labels)."
                        ),
                    },
                    {"role": "user", "content": content},
                ],
            )
            raw = resp.choices[0].message.content if resp.choices else "{}"
            data = json.loads(raw or "{}")
            if not isinstance(data, dict):
                return None
            return data
        except Exception as exc:  # pragma: no cover
            self.logger.error("OpenAI analysis failed: %s", exc)
            return None

    @staticmethod
    def _build_prompt(sentence: str, language: Optional[str]) -> str:
        lang = language or "english"
        return (
            "Analyze this sentence for criminal/illegal/suspicious meaning. "
            "If suspicious, identify 1-3 concise flags. "
            f"Language hint: {lang}.\n"
            f"Sentence: {sentence}"
        )
