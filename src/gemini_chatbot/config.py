import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "gemini-3.1-flash-lite"
_PLACEHOLDER_KEYS = {"", "your_api_key_here"}


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    api_key: str
    model: str = DEFAULT_MODEL


def load_settings(dotenv_path: Path | None = None) -> Settings:
    """Load Gemini API settings from `.env` and environment variables."""
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key in _PLACEHOLDER_KEYS:
        raise ValueError(
            "GEMINI_API_KEY가 설정되지 않았습니다. "
            ".env 파일에 Google AI Studio(https://aistudio.google.com/apikey)에서 "
            "발급받은 API 키를 입력해 주세요."
        )

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    return Settings(api_key=api_key, model=model)
