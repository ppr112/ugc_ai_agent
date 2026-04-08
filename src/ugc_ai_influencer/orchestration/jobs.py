from __future__ import annotations

import logging
import time
from collections.abc import Callable

from ugc_ai_influencer.creative_strategy.service import CreativeStrategyService
from ugc_ai_influencer.input_ingestion.service import InputIngestionService
from ugc_ai_influencer.media_generation.service import MediaGenerationService
from ugc_ai_influencer.models import JobRecord, JobStatus
from ugc_ai_influencer.script_engine.service import ScriptEngineService
from ugc_ai_influencer.storage.repository import JobRepository

logger = logging.getLogger(__name__)


class JobOrchestrator:
    def __init__(
        self,
        ingestion_service: InputIngestionService,
        creative_strategy_service: CreativeStrategyService,
        script_engine_service: ScriptEngineService,
        media_generation_service: MediaGenerationService,
        job_repository: JobRepository,
        retries: int = 2,
    ) -> None:
        self.ingestion_service = ingestion_service
        self.creative_strategy_service = creative_strategy_service
        self.script_engine_service = script_engine_service
        self.media_generation_service = media_generation_service
        self.job_repository = job_repository
        self.retries = retries

    def process_message(self, message_text: str, user_id: str, chat_id: str) -> JobRecord:
        job = JobRecord(user_id=user_id, chat_id=chat_id)
        job.mark(JobStatus.PROCESSING)
        self.job_repository.save(job)

        try:
            job.source_brief = self._run_with_retry(
                lambda: self.ingestion_service.parse(message_text),
                "ingestion",
            )
            job.strategy = self._run_with_retry(
                lambda: self.creative_strategy_service.generate(job.source_brief),
                "creative strategy",
            )
            job.script_package = self._run_with_retry(
                lambda: self.script_engine_service.generate(job.source_brief, job.strategy),
                "script engine",
            )
            job.media_artifact = self._run_with_retry(
                lambda: self.media_generation_service.generate(
                    job.job_id,
                    job.source_brief,
                    job.strategy,
                    job.script_package,
                ),
                "media generation",
            )
            job.mark(JobStatus.READY)
        except Exception as exc:  # pragma: no cover - safety net
            logger.exception("Job failed")
            job.mark(JobStatus.FAILED, str(exc))
        finally:
            self.job_repository.save(job)

        return job

    def _run_with_retry(self, action: Callable[[], object], step_name: str) -> object:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 2):
            try:
                return action()
            except Exception as exc:  # pragma: no cover - safety net
                last_error = exc
                logger.warning("Step %s failed on attempt %s: %s", step_name, attempt, exc)
                time.sleep(0.2 * attempt)

        assert last_error is not None
        raise last_error
