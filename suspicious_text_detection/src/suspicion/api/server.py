from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from ..aggregator import SuspicionAnalyzer, DetectionResult


class AnalyzeRequest(BaseModel):
    text: str
    language: Optional[str] = "auto"
    use_openai: Optional[bool] = None


class AnalyzeResponse(BaseModel):
    sentences: int
    results: List[DetectionResult]  # type: ignore


app = FastAPI(title="Suspicious Text Detection API", version="0.1.0")
_analyzer = SuspicionAnalyzer()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/detect", response_model=AnalyzeResponse)
async def detect(req: AnalyzeRequest):
    language = None if not req.language or req.language == "auto" else req.language
    results = await _analyzer.analyze_text(req.text, language=language)
    return {"sentences": len(results), "results": results}


@app.post("/analyze/hybrid", response_model=AnalyzeResponse)
async def analyze_hybrid(req: AnalyzeRequest):
    language = None if not req.language or req.language == "auto" else req.language
    results = await _analyzer.analyze_text(req.text, language=language)
    return {"sentences": len(results), "results": results}
