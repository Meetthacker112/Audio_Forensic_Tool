# Suspicious Text Detection

Multilingual, explainable suspicious/crime-related text detection with hybrid keyword + zero-shot + optional OpenAI semantic analysis. Includes a FastAPI service, structured logs, and tests.

## Features
- Sentence segmentation (spaCy, NLTK fallback)
- Multilingual keyword detection with categories and severity
- Zero-shot fallback (English or multilingual)
- Optional OpenAI semantic layer (async-ready)
- Unified confidence scoring and explanations
- FastAPI endpoints for programmatic use
- Structured JSONL logs and basic analytics hooks

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m nltk.downloader punkt
uvicorn suspicion.api.server:app --reload
```

## API
- GET /health
- POST /detect
  - Body: `{ "text": "...", "language": "auto", "use_openai": false }`
- POST /analyze/hybrid
  - Same body as /detect; returns hybrid results

## Library usage
```python
from suspicion import SuspicionAnalyzer

analyzer = SuspicionAnalyzer()
results = analyzer.analyze_text("He was caught smuggling gold.")
for r in results:
    print(r)
```

## Config
Configure via `.env` or environment variables. See `.env.example`.

## Tests
```bash
pytest -q
```
