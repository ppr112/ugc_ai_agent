from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ugc_ai_influencer.creative_strategy.service import CreativeStrategyService
from ugc_ai_influencer.input_ingestion.service import InputIngestionService
from ugc_ai_influencer.media_generation.service import MediaGenerationService
from ugc_ai_influencer.models import JobStatus
from ugc_ai_influencer.orchestration.jobs import JobOrchestrator
from ugc_ai_influencer.script_engine.service import ScriptEngineService
from ugc_ai_influencer.storage.repository import JobRepository


class JobOrchestratorTests(unittest.TestCase):
    def test_process_message_creates_job_and_render_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            orchestrator = JobOrchestrator(
                ingestion_service=InputIngestionService(),
                creative_strategy_service=CreativeStrategyService(),
                script_engine_service=ScriptEngineService(),
                media_generation_service=MediaGenerationService(root / "output"),
                job_repository=JobRepository(root / "jobs"),
            )

            job = orchestrator.process_message(
                "Make me a 20-second skincare UGC ad",
                user_id="u1",
                chat_id="c1",
            )

            self.assertEqual(job.status, JobStatus.READY)
            self.assertIsNotNone(job.media_artifact)
            package_path = Path(job.media_artifact.package_path)
            self.assertTrue(package_path.exists())

            package = json.loads(package_path.read_text(encoding="utf-8"))
            self.assertEqual(package["job_id"], job.job_id)
            self.assertEqual(package["brief"]["desired_duration_seconds"], 20)
