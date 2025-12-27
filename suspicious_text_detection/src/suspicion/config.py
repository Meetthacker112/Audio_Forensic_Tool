from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    use_openai: bool
    openai_model: str
    openai_api_key: Optional[str]
    max_concurrency: int
    keywords_path: Path
    logs_path: Path
    cache_dir: Path
    enable_translation: bool
    zero_shot_model_en: str
    zero_shot_model_multi: str
    zero_shot_multilingual: bool


def load_config() -> Config:
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data"
    logs_dir = repo_root / "logs"
    cache_dir = repo_root / ".cache"
    keywords_path = Path(os.getenv("KEYWORDS_PATH", str(data_dir / "crime_keywords.json")))

    return Config(
        use_openai=_parse_bool(os.getenv("USE_OPENAI"), default=False),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_concurrency=int(os.getenv("MAX_CONCURRENCY", "4")),
        keywords_path=keywords_path,
        logs_path=Path(os.getenv("LOGS_PATH", str(logs_dir / "analysis_log.jsonl"))),
        cache_dir=Path(os.getenv("CACHE_DIR", str(cache_dir))),
        enable_translation=_parse_bool(os.getenv("ENABLE_TRANSLATION"), default=False),
        zero_shot_model_en=os.getenv("ZERO_SHOT_MODEL_EN", "facebook/bart-large-mnli"),
        zero_shot_model_multi=os.getenv("ZERO_SHOT_MODEL_MULTI", "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"),
        zero_shot_multilingual=_parse_bool(os.getenv("ZERO_SHOT_MULTILINGUAL"), default=True),
    )
