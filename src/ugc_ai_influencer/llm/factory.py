from __future__ import annotations

from ugc_ai_influencer.config import Settings
from ugc_ai_influencer.llm.client import LLMClient, MockLLMClient, OpenAIResponsesClient


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        return OpenAIResponsesClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
    return MockLLMClient()
