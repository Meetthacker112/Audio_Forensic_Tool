"""
Demo script for hybrid suspicious/crime detection with sentence segmentation.

Run:
    python -m test_detection
or:
    python test_detection.py

It uses spaCy if available (falls back to NLTK/regex). When USE_OPENAI=true and
OPENAI_API_KEY is set, AI-based semantic detection augments keyword-based flags.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from text_detection import (
    detect_suspicious_sentences,
    segment_sentences,
    analyze_text_hybrid_sync,
)


def demo_text() -> str:
    return (
        "He was caught smuggling gold across the border. "
        "The officer reported the crime immediately. "
        "He hacked into a government database and deleted records. "
        "Dr. Smith said it was unusual, but not impossible."
    )


def print_results(text: str) -> None:
    sents: List[str] = segment_sentences(text)
    print(f"Sentences detected: {len(sents)}\n")
    for idx, s in enumerate(sents, 1):
        print(f"{idx}. {s}")

    # Keyword-only layer output
    flagged = detect_suspicious_sentences(text)
    if flagged:
        print("\nKeyword-based suspicious sentences:\n")
        for item in flagged:
            print(f"\"{item.sentence}\" -> Flag: {item.flags}")
    else:
        print("\nNo keyword-based matches; trying OpenAI if enabled...\n")

    # Hybrid output (keywords + OpenAI if enabled)
    hybrid = analyze_text_hybrid_sync(text)
    if not hybrid:
        print("No suspicious sentences detected by hybrid analyzer.")
        return
    print("Hybrid results (JSON-like):\n")
    for res in hybrid:
        print({
            "sentence": res.sentence,
            "detected_by": res.detected_by,
            "confidence": round(res.confidence, 2),
            "flags": res.flags,
        })


if __name__ == "__main__":
    print_results(demo_text())
