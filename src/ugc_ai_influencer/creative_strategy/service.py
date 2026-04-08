from __future__ import annotations

from ugc_ai_influencer.llm.client import LLMClient, LLMRequest, MockLLMClient
from ugc_ai_influencer.models import CreativeStrategy, SourceBrief


class CreativeStrategyService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or MockLLMClient()

    def generate(self, brief: SourceBrief) -> CreativeStrategy:
        if not isinstance(self.llm_client, MockLLMClient):
            return self._generate_with_llm(brief)

        product = brief.product.title()
        angles = [
            f"Problem-solution: show how {product} removes friction from the user's routine",
            f"Creator testimonial: frame {product} as a real recommendation from daily use",
            f"Before-after transformation: focus on the visible payoff after using {product}",
            f"Myth-busting: address doubts that make shoppers hesitate before buying {product}",
            f"Fast demo: show the product value within the first 3 seconds",
        ]
        hooks = [
            f"I almost skipped {product}, but this changed my mind.",
            f"If you're tired of wasting money on overhyped picks, watch this.",
            f"This is the quickest way to explain why {product} stands out.",
        ]
        cta = f"Try {product} now and see if it fits your routine."
        return CreativeStrategy(
            primary_angle=angles[0],
            angles=angles,
            hooks=hooks,
            cta=cta,
        )

    def _generate_with_llm(self, brief: SourceBrief) -> CreativeStrategy:
        schema = {
            "type": "object",
            "properties": {
                "primary_angle": {"type": "string"},
                "angles": {"type": "array", "items": {"type": "string"}},
                "hooks": {"type": "array", "items": {"type": "string"}},
                "cta": {"type": "string"},
            },
            "required": ["primary_angle", "angles", "hooks", "cta"],
            "additionalProperties": False,
        }
        request = LLMRequest(
            system_prompt=(
                "You are a senior UGC ad strategist. Return JSON only. Create practical, "
                "specific short-form ad strategy for a Telegram-driven creator workflow."
            ),
            user_prompt=(
                f"Create strategy for this brief:\n"
                f"- Product: {brief.product}\n"
                f"- Audience: {brief.audience}\n"
                f"- Pain points: {brief.pain_points}\n"
                f"- Benefits: {brief.benefits}\n"
                f"- Tone: {brief.tone}\n"
                f"- Duration: {brief.desired_duration_seconds}\n"
                f"- Source summary: {brief.source_summary}\n"
                f"- Source notes: {brief.fetched_source_notes}\n"
            ),
            schema_name="ugc_creative_strategy",
            schema=schema,
        )
        result = self.llm_client.generate_json(request)
        return CreativeStrategy(
            primary_angle=result["primary_angle"],
            angles=result["angles"],
            hooks=result["hooks"],
            cta=result["cta"],
        )
