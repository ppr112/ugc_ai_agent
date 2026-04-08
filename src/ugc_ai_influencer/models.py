from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InputKind(StrEnum):
    TEXT = "text"
    URL = "url"
    MIXED = "mixed"


class JobStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(slots=True)
class SourceBrief:
    raw_input: str
    input_kind: InputKind
    extracted_urls: list[str]
    fetched_source_notes: list[str]
    product: str
    audience: str
    pain_points: list[str]
    benefits: list[str]
    tone: str
    desired_duration_seconds: int
    source_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CreativeStrategy:
    primary_angle: str
    angles: list[str]
    hooks: list[str]
    cta: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScriptPackage:
    scripts: list[str]
    shot_plan: list[str]
    avatar_prompt: str
    rendering_notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MediaArtifact:
    provider: str
    package_path: str
    status_message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JobRecord:
    job_id: str = field(default_factory=lambda: uuid4().hex)
    user_id: str = "unknown"
    chat_id: str = "unknown"
    status: JobStatus = JobStatus.RECEIVED
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    source_brief: SourceBrief | None = None
    strategy: CreativeStrategy | None = None
    script_package: ScriptPackage | None = None
    media_artifact: MediaArtifact | None = None
    error_message: str | None = None

    def mark(self, status: JobStatus, error_message: str | None = None) -> None:
        self.status = status
        self.updated_at = utc_now()
        self.error_message = error_message

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_brief": self.source_brief.to_dict() if self.source_brief else None,
            "strategy": self.strategy.to_dict() if self.strategy else None,
            "script_package": self.script_package.to_dict() if self.script_package else None,
            "media_artifact": self.media_artifact.to_dict() if self.media_artifact else None,
            "error_message": self.error_message,
        }
