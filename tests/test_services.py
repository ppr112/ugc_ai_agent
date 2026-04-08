from __future__ import annotations

import unittest

from ugc_ai_influencer.creative_strategy.service import CreativeStrategyService
from ugc_ai_influencer.input_ingestion.service import InputIngestionService
from ugc_ai_influencer.llm.client import LLMClient, LLMRequest
from ugc_ai_influencer.script_engine.service import ScriptEngineService


class StubLLMClient(LLMClient):
    def generate_json(self, request: LLMRequest) -> dict:
        if request.schema_name == "ugc_creative_strategy":
            return {
                "primary_angle": "Testimonial-led trust angle",
                "angles": ["Angle 1", "Angle 2", "Angle 3"],
                "hooks": ["Hook 1", "Hook 2", "Hook 3"],
                "cta": "Buy now",
            }
        return {
            "scripts": ["Script 1", "Script 2", "Script 3"],
            "shot_plan": ["Scene 1", "Scene 2"],
            "avatar_prompt": "Creator prompt",
            "rendering_notes": ["Note 1", "Note 2"],
        }


class ServiceGenerationTests(unittest.TestCase):
    def test_llm_backed_services_return_structured_content(self) -> None:
        brief = InputIngestionService().parse("Make me a 20-second skincare UGC ad")
        llm_client = StubLLMClient()

        strategy = CreativeStrategyService(llm_client=llm_client).generate(brief)
        script_package = ScriptEngineService(llm_client=llm_client).generate(brief, strategy)

        self.assertEqual(strategy.primary_angle, "Testimonial-led trust angle")
        self.assertEqual(len(script_package.scripts), 3)
        self.assertEqual(script_package.avatar_prompt, "Creator prompt")
