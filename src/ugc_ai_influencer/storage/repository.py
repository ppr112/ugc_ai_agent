from __future__ import annotations

import json
from pathlib import Path

from ugc_ai_influencer.models import JobRecord


class JobRepository:
    def __init__(self, jobs_dir: Path) -> None:
        self.jobs_dir = jobs_dir
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, job: JobRecord) -> Path:
        target = self.jobs_dir / f"{job.job_id}.json"
        target.write_text(json.dumps(job.to_dict(), indent=2), encoding="utf-8")
        return target
