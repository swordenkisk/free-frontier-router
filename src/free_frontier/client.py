"""OpenRouter API client with bounded retries."""

from __future__ import annotations

import os
import random
import time
from typing import Any

import httpx


API_URL = "https://openrouter.ai/api/v1/chat/completions"
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class OpenRouterError(RuntimeError):
    """Raised when an OpenRouter request cannot be completed."""


class OpenRouterClient:
    """Send chat-completion requests to OpenRouter."""

    def __init__(
        self,
        api_key: str,
        model: str = "openrouter/free",
        timeout: float = 60.0,
        site_url: str | None = None,
        app_name: str = "Free Frontier Router",
        max_retries: int = 3,
    ) -> None:
        if not api_key.strip():
            raise ValueError("An OpenRouter API key is required.")
        if not model.strip():
            raise ValueError("The model name cannot be empty.")
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")
        if max_retries < 0:
            raise ValueError("Max retries cannot be negative.")

        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": app_name,
        }
        if site_url:
            self.headers["HTTP-Referer"] = site_url

    def chat(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Return the assistant response for a list of chat messages."""
        if not messages:
            raise ValueError("At least one chat message is required.")
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1.")
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2.")

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout,
                )
            except httpx.RequestError as exc:
                if attempt == self.max_retries:
                    raise OpenRouterError(f"Network request failed: {exc}") from exc
                self._wait(attempt)
                continue

            if response.status_code in RETRYABLE_STATUS_CODES:
                if attempt == self.max_retries:
                    raise OpenRouterError(
                        self._format_http_error(response)
                    )
                self._wait(attempt, response.headers.get("Retry-After"))
                continue

            if not response.is_success:
                raise OpenRouterError(self._format_http_error(response))

            try:
                data: dict[str, Any] = response.json()
                content = data["choices"][0]["message"]["content"]
            except (ValueError, KeyError, IndexError, TypeError) as exc:
                raise OpenRouterError(
                    "OpenRouter returned an unexpected response format."
                ) from exc

            if not isinstance(content, str) or not content.strip():
                raise OpenRouterError("The model returned an empty response.")

            return content.strip()

        raise OpenRouterError("Request failed after all retry attempts.")

    @staticmethod
    def _wait(attempt: int, retry_after: str | None = None) -> None:
        """Wait before retrying, using Retry-After when it is valid."""
        if retry_after:
            try:
                delay = min(max(float(retry_after), 0.0), 30.0)
            except ValueError:
                delay = 0.0
            if delay:
                time.sleep(delay)
                return

        delay = min(2**attempt + random.uniform(0.0, 0.5), 30.0)
        time.sleep(delay)

    @staticmethod
    def _format_http_error(response: httpx.Response) -> str:
        """Create a concise error message without exposing request secrets."""
        body = response.text.strip().replace("\n", " ")
        if len(body) > 500:
            body = body[:497] + "..."
        detail = f": {body}" if body else ""
        return f"OpenRouter returned HTTP {response.status_code}{detail}"


def client_from_environment() -> OpenRouterClient:
    """Build a client from environment variables."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Add it to your .env file."
        )

    try:
        timeout = float(os.getenv("OPENROUTER_TIMEOUT", "60"))
    except ValueError as exc:
        raise ValueError("OPENROUTER_TIMEOUT must be a number.") from exc

    return OpenRouterClient(
        api_key=api_key,
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        timeout=timeout,
        site_url=os.getenv("OPENROUTER_SITE_URL") or None,
        app_name=os.getenv("OPENROUTER_APP_NAME", "Free Frontier Router"),
    )
