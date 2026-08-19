from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from medical_ai.agent.llm_config import LLMConfig, get_llm_config


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class OpenAICompatibleClient:
    def __init__(self, config: LLMConfig | None = None, timeout_seconds: int = 60, max_retries: int = 2) -> None:
        self.config = config or get_llm_config()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def chat_json(self, messages: list[ChatMessage], max_tokens: int = 1200) -> str:
        if not self.config.configured:
            raise RuntimeError("LLM is not configured. Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL in .env.")

        payload = {
            "model": self.config.model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": 0,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            url=self._chat_completions_url(),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        last_error: urllib.error.URLError | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    body = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"LLM API HTTP {exc.code}: {detail}") from exc
            except urllib.error.URLError as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise RuntimeError(f"LLM API request failed: {exc.reason}") from exc
                time.sleep(1.0 * (attempt + 1))
        else:
            raise RuntimeError(f"LLM API request failed: {last_error}")

        return self._extract_content(body)

    def _chat_completions_url(self) -> str:
        return f"{self.config.base_url.rstrip('/')}/chat/completions"

    def _extract_content(self, body: dict[str, Any]) -> str:
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected LLM API response shape: {body}") from exc
