from suspicion import SuspicionAnalyzer


def main():
    analyzer = SuspicionAnalyzer()
    text = (
        "He was caught smuggling gold across the border. "
        "The officer reported the crime immediately. "
        "He hacked into a government database and deleted records. "
        "Dr. Smith said it was unusual, but not impossible."
    )
    results = analyzer.analyze_text_sync(text)
    for res in results:
        print({
            "sentence": res.sentence,
            "detected_by": res.detected_by,
            "confidence": round(res.confidence, 2),
            "flags": res.flags,
            "labels": res.labels,
        })


if __name__ == "__main__":
    main()
