from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(slots=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str
    schema_name: str
    schema: dict


class LLMClient:
    def generate_json(self, request: LLMRequest) -> dict:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    def generate_json(self, request: LLMRequest) -> dict:
        del request
        return {}


class OpenAIResponsesClient(LLMClient):
    def __init__(self, api_key: str, model: str, timeout_seconds: int = 20) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate_json(self, request: LLMRequest) -> dict:
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": request.schema_name,
                    "strict": True,
                    "schema": request.schema,
                }
            },
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
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc

        data = json.loads(raw)
        output_text = data.get("output_text")
        if output_text:
            return json.loads(output_text)

        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    return json.loads(content["text"])

        raise RuntimeError("OpenAI response did not contain structured JSON output.")
