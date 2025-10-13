"""Suspicious text detection package.

Exports high-level analyzer for easy use.
"""
from .aggregator import SuspicionAnalyzer, DetectionResult
from .segmenter import SentenceSegmenter, detect_language
from .keywords import KeywordStore

__all__ = [
    "SuspicionAnalyzer",
    "DetectionResult",
    "SentenceSegmenter",
    "detect_language",
    "KeywordStore",
]

__version__ = "0.1.0"
