"""OpenAI-compatible chat client (FR-TUTOR-4): Ollama, vLLM, or hosted —
one config, streaming, no SDK dependency (plain httpx)."""

import json
from collections.abc import AsyncIterator

import httpx

from ..core.config import get_settings


class ProviderUnavailable(Exception):
    pass


async def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    """Yield content tokens from /chat/completions (SSE). Raises
    ProviderUnavailable on connection/HTTP errors so callers can degrade."""
    s = get_settings()
    headers = {"Content-Type": "application/json"}
    if s.ember_api_key:
        headers["Authorization"] = f"Bearer {s.ember_api_key}"

    try:
        async with httpx.AsyncClient(timeout=s.ember_timeout_s) as client:
            async with client.stream(
                "POST",
                f"{s.ember_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json={"model": s.ember_model, "messages": messages, "stream": True},
            ) as resp:
                if resp.status_code != 200:
                    raise ProviderUnavailable(f"provider returned {resp.status_code}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    payload = line.removeprefix("data:").strip()
                    if payload == "[DONE]":
                        return
                    try:
                        delta = json.loads(payload)["choices"][0]["delta"]
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    token = delta.get("content")
                    if token:
                        yield token
    except (httpx.HTTPError, OSError) as exc:
        raise ProviderUnavailable(str(exc)) from exc
