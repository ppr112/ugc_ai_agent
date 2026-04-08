from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue

        key, value = raw.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str = ""
    openai_api_key: str = ""
    llm_provider: str = "mock"
    openai_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4.1-mini"
    media_provider: str = "mock"
    output_dir: Path = Path("./data/output")
    jobs_dir: Path = Path("./data/jobs")
    uploads_dir: Path = Path("./data/uploads")
    log_level: str = "INFO"
    request_timeout_seconds: int = 20

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv()
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            llm_provider=os.getenv("LLM_PROVIDER", "mock"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini"),
            media_provider=os.getenv("MEDIA_PROVIDER", "mock"),
            output_dir=Path(os.getenv("OUTPUT_DIR", "./data/output")),
            jobs_dir=Path(os.getenv("JOBS_DIR", "./data/jobs")),
            uploads_dir=Path(os.getenv("UPLOADS_DIR", "./data/uploads")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        )
