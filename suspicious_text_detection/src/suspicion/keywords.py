from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import re

from .config import load_config


_SEVERITY_BY_CATEGORY: Dict[str, str] = {
    "violence": "CRITICAL",
    "weapons": "HIGH",
    "threats": "HIGH",
    "kidnapping": "HIGH",
    "drugs": "MEDIUM",
    "theft": "MEDIUM",
    "fraud": "MEDIUM",
    "smuggling": "MEDIUM",
    "general": "LOW",
}


@dataclass(frozen=True)
class KeywordHit:
    keyword: str
    category: str
    severity: str


class KeywordStore:
    """Loads keyword dictionary and compiles regex patterns per language."""

    def __init__(self, keywords_path: Optional[Path | str] = None) -> None:
        cfg = load_config()
        self.keywords_path = Path(keywords_path) if keywords_path else cfg.keywords_path
        self.keywords: Dict[str, Dict[str, List[str]]] = self._load_keywords(self.keywords_path)
        self._compiled_cache: Dict[str, List[Tuple[str, str, re.Pattern[str]]]] = {}

    @staticmethod
    def _load_keywords(path: Path) -> Dict[str, Dict[str, List[str]]]:
        if not path.exists():
            return {
                "english": {
                    "violence": ["murder", "kill", "attack"],
                    "theft": ["theft", "robbery", "steal"],
                    "weapons": ["weapon", "gun", "knife"],
                    "fraud": ["fraud", "scam", "embezzle"],
                    "smuggling": ["smuggle", "smuggling"],
                    "general": ["crime", "illegal"],
                    "threats": ["threat", "threaten"],
                }
            }
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("crime_keywords.json must contain a dict at top-level")
            return data  # type: ignore

    @staticmethod
    def _keyword_to_pattern(keyword: str) -> str:
        if " " in keyword.strip():
            return rf"\b{re.escape(keyword)}\b"
        return rf"\b{re.escape(keyword)}\w*\b"

    def _compile_for_language(self, language: str) -> List[Tuple[str, str, re.Pattern[str]]]:
        lang = language.lower()
        if lang in self._compiled_cache:
            return self._compiled_cache[lang]
        compiled: List[Tuple[str, str, re.Pattern[str]]] = []
        lang_dict = self.keywords.get(lang, {})
        for category, items in lang_dict.items():
            for kw in items:
                pat = re.compile(self._keyword_to_pattern(kw), flags=re.IGNORECASE)
                compiled.append((category, kw, pat))
        self._compiled_cache[lang] = compiled
        return compiled

    def find_flags(self, sentence: str, language: Optional[str] = None) -> List[KeywordHit]:
        lang = (language or "english").lower()
        patterns = self._compile_for_language(lang)
        sent = sentence.strip()
        hits: List[KeywordHit] = []
        for category, kw, pat in patterns:
            if pat.search(sent) is not None:
                severity = _SEVERITY_BY_CATEGORY.get(category, "LOW")
                hits.append(KeywordHit(keyword=kw, category=category, severity=severity))
        # Deduplicate by keyword
        seen: set[str] = set()
        unique: List[KeywordHit] = []
        for h in hits:
            if h.keyword not in seen:
                unique.append(h)
                seen.add(h.keyword)
        return unique

    def categories(self) -> List[str]:
        cats: List[str] = []
        for lang_dict in self.keywords.values():
            for cat in lang_dict.keys():
                if cat not in cats:
                    cats.append(cat)
        return cats
