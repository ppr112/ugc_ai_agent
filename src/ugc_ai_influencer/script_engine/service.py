from __future__ import annotations

from ugc_ai_influencer.llm.client import LLMClient, LLMRequest, MockLLMClient
from ugc_ai_influencer.models import CreativeStrategy, ScriptPackage, SourceBrief


class ScriptEngineService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or MockLLMClient()

    def generate(self, brief: SourceBrief, strategy: CreativeStrategy) -> ScriptPackage:
        if not isinstance(self.llm_client, MockLLMClient):
            return self._generate_with_llm(brief, strategy)

        product = brief.product.title()
        duration = brief.desired_duration_seconds

        scripts = [
            (
                f"Hook: {strategy.hooks[0]} "
                f"I wanted something that solved {brief.pain_points[0].lower()}. "
                f"{product} stood out because {brief.benefits[0].lower()}. "
                f"After trying it, the biggest win was how natural it felt in my day. "
                f"{strategy.cta}"
            ),
            (
                f"Hook: {strategy.hooks[1]} "
                f"Most products promise too much, but {product} keeps the message simple. "
                f"It helps with {brief.pain_points[-1].lower()} and gives "
                f"{brief.benefits[-1].lower()}. {strategy.cta}"
            ),
            (
                f"Hook: {strategy.hooks[2]} "
                f"For a {duration}-second ad, start with the problem, show the product fast, "
                f"then land on the proof point: {brief.benefits[0]}. {strategy.cta}"
            ),
        ]

        shot_plan = [
            "Scene 1: Selfie-style opener with strong hook in the first 2 seconds",
            "Scene 2: Close-up of the product or website while describing the core problem",
            "Scene 3: Quick demo or proof moment focused on the main benefit",
            "Scene 4: Direct-to-camera CTA with creator-style confidence",
        ]

        avatar_prompt = (
            f"Friendly UGC creator, late-20s energy, conversational delivery, vertical video, "
            f"bright natural lighting, authentic bedroom or bathroom setting, tone: {brief.tone}."
        )

        rendering_notes = [
            f"Target duration: {duration} seconds",
            "Format: 9:16 vertical short-form video",
            "Delivery style: authentic handheld UGC creator ad",
            "Include burned-in captions optimized for social retention",
        ]

        return ScriptPackage(
            scripts=scripts,
            shot_plan=shot_plan,
            avatar_prompt=avatar_prompt,
            rendering_notes=rendering_notes,
        )

    def _generate_with_llm(
        self,
        brief: SourceBrief,
        strategy: CreativeStrategy,
    ) -> ScriptPackage:
        schema = {
            "type": "object",
            "properties": {
                "scripts": {"type": "array", "items": {"type": "string"}},
                "shot_plan": {"type": "array", "items": {"type": "string"}},
                "avatar_prompt": {"type": "string"},
                "rendering_notes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["scripts", "shot_plan", "avatar_prompt", "rendering_notes"],
            "additionalProperties": False,
        }
        request = LLMRequest(
            system_prompt=(
                "You are a senior UGC scriptwriter. Return JSON only. Write creator-native "
                "scripts that sound authentic, specific, and direct."
            ),
            user_prompt=(
                f"Write three UGC ad scripts plus a shot plan.\n"
                f"- Product: {brief.product}\n"
                f"- Audience: {brief.audience}\n"
                f"- Pain points: {brief.pain_points}\n"
                f"- Benefits: {brief.benefits}\n"
                f"- Tone: {brief.tone}\n"
                f"- Duration: {brief.desired_duration_seconds} seconds\n"
                f"- Primary angle: {strategy.primary_angle}\n"
                f"- Hooks: {strategy.hooks}\n"
                f"- CTA: {strategy.cta}\n"
                f"- Source summary: {brief.source_summary}\n"
                f"- Source notes: {brief.fetched_source_notes}\n"
            ),
            schema_name="ugc_script_package",
            schema=schema,
        )
        result = self.llm_client.generate_json(request)
        return ScriptPackage(
            scripts=result["scripts"],
            shot_plan=result["shot_plan"],
            avatar_prompt=result["avatar_prompt"],
            rendering_notes=result["rendering_notes"],
        )
