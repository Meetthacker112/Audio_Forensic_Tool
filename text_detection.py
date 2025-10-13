"""
Text Detection Module

Provides:
- Accurate sentence boundary detection (spaCy if available, NLTK/regex fallback)
- Suspicious/Crime-related word detection using a configurable JSON keyword list

Design goals:
- Modular, reusable, importable anywhere in the repo
- Extends existing pipeline without overwriting; can be used alongside existing modules
- Python 3.10+, PEP8 compliant, documented
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import json
import re

# Optional imports; fallbacks are handled gracefully
try:
    import spacy  # type: ignore
    _SPACY_AVAILABLE = True
except Exception:  # pragma: no cover - runtime environment may lack spaCy
    spacy = None  # type: ignore
    _SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize.punkt import PunktSentenceTokenizer
except Exception:  # pragma: no cover
    nltk = None  # type: ignore
    PunktSentenceTokenizer = None  # type: ignore

try:
    from langdetect import detect  # lightweight language detection
except Exception:  # pragma: no cover
    detect = None  # type: ignore


_DEFAULT_ABBREVIATIONS_EN = {
    # Common English abbreviations that should not split sentences
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs",
    "inc", "ltd", "co", "corp", "dept", "est",
    "e.g", "i.e", "etc", "fig", "no", "nos",
    # Months/Days
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "mon", "tue", "wed", "thu", "fri", "sat", "sun",
}


def _ensure_nltk_resources() -> None:
    """Ensure required NLTK resources are available (quietly)."""
    if nltk is None:
        return
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        # Non-fatal; regex fallback will handle
        pass


def _detect_language(text: str) -> str:
    """Detect language with langdetect; fallback to script heuristics; default to english."""
    cleaned = text.strip()
    if not cleaned:
        return "english"

    # Try langdetect if available
    if detect is not None:
        try:
            code = detect(cleaned)
            mapping = {"en": "english", "hi": "hindi", "gu": "gujarati"}
            if code in mapping:
                return mapping[code]
        except Exception:
            pass

    # Script-based heuristic
    if re.search(r"[\u0A80-\u0AFF]", cleaned):  # Gujarati
        return "gujarati"
    if re.search(r"[\u0900-\u097F]", cleaned):  # Devanagari (Hindi)
        return "hindi"
    return "english"


class SentenceSegmenter:
    """Sentence segmentation with spaCy if available, otherwise NLTK/regex.

    - spaCy path: tries `xx_sent_ud_sm` (multilingual) then `en_core_web_sm` for English
    - NLTK path: uses Punkt with enriched abbreviation list for English
    - Regex fallback: punctuation-based splitting for Hindi/Gujarati/others
    """

    def __init__(self, prefer_spacy: bool = True) -> None:
        self.prefer_spacy = prefer_spacy
        self._spacy_nlp = None
        self._init_spacy_pipeline()
        _ensure_nltk_resources()

        # Precompile regex for Indic sentence boundaries
        self._indic_splitter = re.compile(r"(?<=[\.!?।])\s+")

    def _init_spacy_pipeline(self) -> None:
        if not self.prefer_spacy or not _SPACY_AVAILABLE:
            return
        try:
            # Best default: multilingual sentence segmenter (tiny model)
            self._spacy_nlp = spacy.load("xx_sent_ud_sm")  # type: ignore
        except Exception:
            try:
                # Fallback: English small model
                self._spacy_nlp = spacy.load("en_core_web_sm")  # type: ignore
            except Exception:
                self._spacy_nlp = None

    def _segment_with_spacy(self, text: str) -> List[str]:
        if not self._spacy_nlp:
            return []
        doc = self._spacy_nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    def _segment_with_nltk(self, text: str) -> List[str]:
        if nltk is None:
            return []
        # Use English Punkt and add extra abbreviations for robustness
        try:
            tokenizer: PunktSentenceTokenizer = nltk.data.load("tokenizers/punkt/english.pickle")  # type: ignore
            tokenizer._params.abbrev_types.update(_DEFAULT_ABBREVIATIONS_EN)  # type: ignore
            return [s.strip() for s in tokenizer.tokenize(text) if s.strip()]
        except Exception:
            # Generic fallback
            return [s.strip() for s in re.split(self._indic_splitter, text) if s.strip()]

    def _segment_indic(self, text: str) -> List[str]:
        # Split on ., !, ?, and danda (।) while keeping quotes attached
        raw = [s.strip() for s in re.split(self._indic_splitter, text) if s.strip()]
        return raw

    def segment(self, text: str, language: Optional[str] = None) -> List[str]:
        """Split `text` into sentences with multilingual handling and abbreviation awareness."""
        lang = language or _detect_language(text)

        # Try spaCy first if preferred/available
        if self.prefer_spacy and self._spacy_nlp is not None:
            sents = self._segment_with_spacy(text)
            if sents:
                return sents

        # Language-specific fallbacks
        if lang == "english":
            sents = self._segment_with_nltk(text)
            if sents:
                return sents
            # Last resort
            return [s.strip() for s in re.split(self._indic_splitter, text) if s.strip()]

        # Hindi / Gujarati / Others: regex-based splitting works well
        return self._segment_indic(text)


@dataclass(frozen=True)
class FlaggedSentence:
    sentence: str
    flags: List[str]


class SuspiciousDetector:
    """Detect sentences containing suspicious/crime-related terms.

    Keywords are loaded from a JSON file with the schema:
    {
      "english": {
        "violence": ["murder", "attack"],
        "theft": ["theft", "robbery"],
        ...
      },
      "hindi": { ... },
      "gujarati": { ... }
    }
    """

    def __init__(self, keywords_path: Optional[Path | str] = None) -> None:
        if keywords_path is None:
            # Default to alongside this module
            keywords_path = Path(__file__).with_name("crime_keywords.json")
        self.keywords_path = Path(keywords_path)
        self.keywords: Dict[str, Dict[str, List[str]]] = self._load_keywords(self.keywords_path)
        self._compiled_cache: Dict[str, List[Tuple[str, re.Pattern[str]]]] = {}

    @staticmethod
    def _load_keywords(path: Path) -> Dict[str, Dict[str, List[str]]]:
        if not path.exists():
            # Minimal built-in fallback so the module still works
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
        # If keyword is multi-word, match with boundaries around the phrase
        if " " in keyword.strip():
            return rf"\b{re.escape(keyword)}\b"
        # Single token: match common morphological suffixes (e.g., smuggling/smuggled)
        return rf"\b{re.escape(keyword)}\w*\b"

    def _compile_for_language(self, language: str) -> List[Tuple[str, re.Pattern[str]]]:
        lang = language.lower()
        if lang in self._compiled_cache:
            return self._compiled_cache[lang]

        compiled: List[Tuple[str, re.Pattern[str]]] = []
        lang_dict = self.keywords.get(lang, {})
        for _category, items in lang_dict.items():
            for kw in items:
                pat = re.compile(self._keyword_to_pattern(kw), flags=re.IGNORECASE)
                compiled.append((kw, pat))
        self._compiled_cache[lang] = compiled
        return compiled

    def find_flags_in_sentence(self, sentence: str, language: Optional[str] = None) -> List[str]:
        lang = (language or _detect_language(sentence)).lower()
        patterns = self._compile_for_language(lang)
        found: List[str] = []
        sent = sentence.strip()
        for kw, pat in patterns:
            if pat.search(sent) is not None:
                found.append(kw)
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique = [x for x in found if not (x in seen or seen.add(x))]
        return unique

    def analyze_text(self, text: str, language: Optional[str] = None) -> List[FlaggedSentence]:
        if not text or not text.strip():
            return []
        segmenter = SentenceSegmenter()
        sents = segmenter.segment(text, language=language)
        results: List[FlaggedSentence] = []
        lang = language or _detect_language(text)
        for sent in sents:
            flags = self.find_flags_in_sentence(sent, language=lang)
            if flags:
                results.append(FlaggedSentence(sentence=sent, flags=flags))
        return results


# Convenience functional API
_segmenter_singleton = SentenceSegmenter()
_detector_singleton = SuspiciousDetector()


def segment_sentences(text: str, language: Optional[str] = None) -> List[str]:
    """Segment `text` into sentences. Wrapper around SentenceSegmenter.segment."""
    return _segmenter_singleton.segment(text, language=language)


def detect_suspicious_sentences(text: str, language: Optional[str] = None) -> List[FlaggedSentence]:
    """Return list of sentences containing suspicious/crime-related terms.

    Each item has fields: sentence, flags (matched keywords).
    """
    return _detector_singleton.analyze_text(text, language=language)


__all__ = [
    "SentenceSegmenter",
    "SuspiciousDetector",
    "FlaggedSentence",
    "segment_sentences",
    "detect_suspicious_sentences",
]
