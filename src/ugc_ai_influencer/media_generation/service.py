from __future__ import annotations

import json
from pathlib import Path

from ugc_ai_influencer.models import CreativeStrategy, MediaArtifact, ScriptPackage, SourceBrief


class MediaGenerationService:
    def __init__(self, output_dir: Path, provider: str = "mock") -> None:
        self.output_dir = output_dir
        self.provider = provider
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        job_id: str,
        brief: SourceBrief,
        strategy: CreativeStrategy,
        script_package: ScriptPackage,
    ) -> MediaArtifact:
        package_path = self.output_dir / f"{job_id}_render_package.json"
        payload = {
            "job_id": job_id,
            "provider": self.provider,
            "brief": brief.to_dict(),
            "strategy": strategy.to_dict(),
            "script_package": script_package.to_dict(),
        }
        package_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return MediaArtifact(
            provider=self.provider,
            package_path=str(package_path),
            status_message="Render package created. Ready for downstream video generation.",
        )
