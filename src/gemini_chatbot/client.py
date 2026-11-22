from collections.abc import Iterator
from typing import Any

from google import genai

from gemini_chatbot.config import Settings


def _extract_text_delta(event: Any) -> str | None:
    """Extract text from a streaming `step.delta` event if present."""
    event_type = (
        event.get("event_type")
        if isinstance(event, dict)
        else getattr(event, "event_type", None)
    )
    if event_type != "step.delta":
        return None

    delta = (
        event.get("delta")
        if isinstance(event, dict)
        else getattr(event, "delta", None)
    )
    if delta is None:
        return None

    delta_type = (
        delta.get("type")
        if isinstance(delta, dict)
        else getattr(delta, "type", None)
    )
    if delta_type != "text":
        return None

    text = (
        delta.get("text")
        if isinstance(delta, dict)
        else getattr(delta, "text", None)
    )
    return text if isinstance(text, str) and text else None


class GeminiChatClient:
    """Stateless Gemini terminal chatbot client using the Interactions API."""

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self._model = settings.model
        self._client = client if client is not None else genai.Client(api_key=settings.api_key)

    @property
    def model(self) -> str:
        return self._model

    def send_message_stream(self, user_input: str) -> Iterator[str]:
        """Send a single stateless prompt and yield streamed text chunks."""
        stream = self._client.interactions.create(
            model=self._model,
            input=user_input,
            store=False,
            stream=True,
        )
        for event in stream:
            chunk = _extract_text_delta(event)
            if chunk:
                yield chunk
