"""Basic validation tests for the OpenRouter client."""

import pytest

from free_frontier.client import OpenRouterClient


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        OpenRouterClient(api_key="")


def test_client_rejects_empty_messages() -> None:
    client = OpenRouterClient(api_key="test-key")

    with pytest.raises(ValueError, match="At least one"):
        client.chat(messages=[])


def test_client_rejects_invalid_temperature() -> None:
    client = OpenRouterClient(api_key="test-key")

    with pytest.raises(ValueError, match="temperature"):
        client.chat(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=3.0,
        )
