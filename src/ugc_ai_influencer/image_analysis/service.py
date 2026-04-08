from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ugc_ai_influencer.config import Settings


class ImageAnalyzer:
    def analyze(self, image_path: Path, caption: str = "") -> str:
        raise NotImplementedError


class MockImageAnalyzer(ImageAnalyzer):
    def analyze(self, image_path: Path, caption: str = "") -> str:
        del image_path
        if caption.strip():
            return (
                f"The image likely shows a product the user wants to promote. Caption context: {caption}. "
                "Focus on identifying the product, visible packaging, likely audience, and a creator-style demo angle."
            )
        return (
            "The image likely shows a product or item to promote. Focus on visible packaging, likely use case, "
            "target audience, and an authentic creator-style demonstration angle."
        )


class OpenAIImageAnalyzer(ImageAnalyzer):
    def __init__(self, api_key: str, model: str, timeout_seconds: int = 20) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def analyze(self, image_path: Path, caption: str = "") -> str:
        image_bytes = image_path.read_bytes()
        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "image/jpeg"
        data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        prompt = (
            "Analyze this product image for a UGC-style marketing workflow. "
            "Return one concise paragraph covering: what the product appears to be, visible brand or packaging clues, "
            "likely audience, likely benefits, and the best creator-style ad angle."
        )
        if caption.strip():
            prompt += f" User caption: {caption}"

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
        }
        http_request = Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"OpenAI image analysis failed: {exc}") from exc

        data = json.loads(raw)
        output_text = data.get("output_text")
        if output_text:
            return output_text.strip()

        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    return content["text"].strip()

        raise RuntimeError("OpenAI image analysis did not return text output.")


def build_image_analyzer(settings: Settings) -> ImageAnalyzer:
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        return OpenAIImageAnalyzer(
            api_key=settings.openai_api_key,
            model=settings.openai_vision_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
    return MockImageAnalyzer()
