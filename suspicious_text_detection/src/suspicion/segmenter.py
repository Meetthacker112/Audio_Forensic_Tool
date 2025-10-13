from __future__ import annotations

from typing import List, Optional
import re

# Optional imports; fallbacks are handled gracefully
try:
    import spacy  # type: ignore
    _SPACY_AVAILABLE = True
except Exception:  # pragma: no cover
    spacy = None  # type: ignore
    _SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize.punkt import PunktSentenceTokenizer
except Exception:  # pragma: no cover
    nltk = None  # type: ignore
    PunktSentenceTokenizer = None  # type: ignore

try:
    from langdetect import detect  # type: ignore
except Exception:  # pragma: no cover
    detect = None  # type: ignore


_DEFAULT_ABBREVIATIONS_EN = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs",
    "inc", "ltd", "co", "corp", "dept", "est",
    "e.g", "i.e", "etc", "fig", "no", "nos",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "mon", "tue", "wed", "thu", "fri", "sat", "sun",
}


def _ensure_nltk_resources() -> None:
    if nltk is None:
        return
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        pass


def detect_language(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return "english"
    if detect is not None:
        try:
            code = detect(cleaned)
            mapping = {"en": "english", "hi": "hindi", "gu": "gujarati"}
            if code in mapping:
                return mapping[code]
        except Exception:
            pass
    if re.search(r"[\u0A80-\u0AFF]", cleaned):  # Gujarati
        return "gujarati"
    if re.search(r"[\u0900-\u097F]", cleaned):  # Devanagari (Hindi)
        return "hindi"
    return "english"


class SentenceSegmenter:
    """Sentence segmentation with spaCy if available, otherwise NLTK/regex."""

    def __init__(self, prefer_spacy: bool = True) -> None:
        self.prefer_spacy = prefer_spacy
        self._spacy_nlp = None
        self._init_spacy_pipeline()
        _ensure_nltk_resources()
        self._indic_splitter = re.compile(r"(?<=[\.!?।])\s+")

    def _init_spacy_pipeline(self) -> None:
        if not self.prefer_spacy or not _SPACY_AVAILABLE:
            return
        try:
            self._spacy_nlp = spacy.load("xx_sent_ud_sm")  # type: ignore
        except Exception:
            try:
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
        try:
            tokenizer: PunktSentenceTokenizer = nltk.data.load("tokenizers/punkt/english.pickle")  # type: ignore
            tokenizer._params.abbrev_types.update(_DEFAULT_ABBREVIATIONS_EN)  # type: ignore
            return [s.strip() for s in tokenizer.tokenize(text) if s.strip()]
        except Exception:
            return [s.strip() for s in re.split(self._indic_splitter, text) if s.strip()]

    def _segment_indic(self, text: str) -> List[str]:
        return [s.strip() for s in re.split(self._indic_splitter, text) if s.strip()]

    def segment(self, text: str, language: Optional[str] = None) -> List[str]:
        lang = language or detect_language(text)
        if self.prefer_spacy and self._spacy_nlp is not None:
            sents = self._segment_with_spacy(text)
            if sents:
                return sents
        if lang == "english":
            sents = self._segment_with_nltk(text)
            if sents:
                return sents
            return [s.strip() for s in re.split(self._indic_splitter, text) if s.strip()]
        return self._segment_indic(text)
