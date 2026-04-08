from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ugc_ai_influencer.config import Settings
from ugc_ai_influencer.creative_strategy.service import CreativeStrategyService
from ugc_ai_influencer.image_analysis.service import build_image_analyzer
from ugc_ai_influencer.input_ingestion.fetcher import UrlContentFetcher
from ugc_ai_influencer.input_ingestion.service import InputIngestionService
from ugc_ai_influencer.llm.factory import build_llm_client
from ugc_ai_influencer.logging_config import configure_logging
from ugc_ai_influencer.media_generation.service import MediaGenerationService
from ugc_ai_influencer.orchestration.jobs import JobOrchestrator
from ugc_ai_influencer.script_engine.service import ScriptEngineService
from ugc_ai_influencer.storage.repository import JobRepository
from ugc_ai_influencer.telegram_interface.handlers import (
    build_image_prompt,
    build_job_reply,
    build_start_message,
)

logger = logging.getLogger(__name__)


def build_orchestrator(settings: Settings) -> JobOrchestrator:
    llm_client = build_llm_client(settings)
    return JobOrchestrator(
        ingestion_service=InputIngestionService(
            url_content_fetcher=UrlContentFetcher(settings.request_timeout_seconds),
        ),
        creative_strategy_service=CreativeStrategyService(llm_client=llm_client),
        script_engine_service=ScriptEngineService(llm_client=llm_client),
        media_generation_service=MediaGenerationService(
            output_dir=settings.output_dir,
            provider=settings.media_provider,
        ),
        job_repository=JobRepository(settings.jobs_dir),
    )


def _ensure_dirs(settings: Settings) -> None:
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.jobs_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)


def run_bot() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    _ensure_dirs(settings)

    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing. Add it in your environment or .env.")

    try:
        from telegram import Update
        from telegram.ext import (
            Application,
            CommandHandler,
            ContextTypes,
            MessageHandler,
            filters,
        )
    except ImportError as exc:  # pragma: no cover - local setup safety
        raise RuntimeError(
            "python-telegram-bot is not installed. Run `pip install -e .` first."
        ) from exc

    orchestrator = build_orchestrator(settings)
    image_analyzer = build_image_analyzer(settings)
    application = Application.builder().token(settings.telegram_bot_token).build()

    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if update.message:
            await update.message.reply_text(build_start_message())

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if not update.message or not update.message.text or not update.effective_chat:
            return

        user_id = str(update.effective_user.id) if update.effective_user else "unknown"
        chat_id = str(update.effective_chat.id)
        logger.info("Received text message from user=%s chat=%s", user_id, chat_id)

        job = orchestrator.process_message(update.message.text, user_id=user_id, chat_id=chat_id)
        await update.message.reply_text(build_job_reply(job))

    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if not update.message or not update.message.photo or not update.effective_chat:
            return

        user_id = str(update.effective_user.id) if update.effective_user else "unknown"
        chat_id = str(update.effective_chat.id)
        caption = update.message.caption or ""
        logger.info("Received photo message from user=%s chat=%s", user_id, chat_id)

        await update.message.reply_text("Image received. I’m analyzing it and building your UGC ad package now.")

        largest_photo = update.message.photo[-1]
        telegram_file = await largest_photo.get_file()
        image_path = settings.uploads_dir / f"{largest_photo.file_unique_id}.jpg"
        await telegram_file.download_to_drive(custom_path=str(image_path))

        image_analysis = image_analyzer.analyze(Path(image_path), caption=caption)
        combined_prompt = build_image_prompt(caption, image_analysis)
        job = orchestrator.process_message(combined_prompt, user_id=user_id, chat_id=chat_id)
        await update.message.reply_text(build_job_reply(job))

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot is running")
    application.run_polling()


def main() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        run_bot()
    finally:
        try:
            loop.close()
        except RuntimeError:
            pass


if __name__ == "__main__":
    main()
