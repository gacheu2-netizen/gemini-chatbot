from types import SimpleNamespace

import pytest

from gemini_chatbot.client import GeminiChatClient
from gemini_chatbot.config import DEFAULT_MODEL, Settings, load_settings


class FakeInteractionsAPI:
    def __init__(self, responses: list[list[object]]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> list[object]:
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeGenAIClient:
    def __init__(self, responses: list[list[object]]) -> None:
        self.interactions = FakeInteractionsAPI(responses)


def test_load_settings_missing_key(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        load_settings(dotenv_path=tmp_path / ".env")


def test_load_settings_placeholder_key(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "your_api_key_here")

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        load_settings(dotenv_path=tmp_path / ".env")


def test_load_settings_default_model(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    settings = load_settings(dotenv_path=tmp_path / ".env")
    assert settings.api_key == "test-api-key"
    assert settings.model == DEFAULT_MODEL


def test_send_message_stream_stateless_and_extracts_text() -> None:
    events = [
        SimpleNamespace(
            event_type="interaction.created",
            interaction=SimpleNamespace(id="int_001"),
        ),
        SimpleNamespace(
            event_type="step.delta",
            delta=SimpleNamespace(type="thought_signature", signature="sig"),
        ),
        SimpleNamespace(
            event_type="step.delta",
            delta=SimpleNamespace(type="text", text="안녕"),
        ),
        SimpleNamespace(
            event_type="step.delta",
            delta=SimpleNamespace(type="text", text="하세요!"),
        ),
        SimpleNamespace(
            event_type="interaction.completed",
            interaction=SimpleNamespace(id="int_001"),
        ),
    ]
    fake_client = FakeGenAIClient([events])
    chat = GeminiChatClient(
        Settings(api_key="test-key", model="gemini-3.1-flash-lite"),
        client=fake_client,
    )

    chunks = list(chat.send_message_stream("인사해줘"))

    assert chunks == ["안녕", "하세요!"]
    assert len(fake_client.interactions.calls) == 1
    call = fake_client.interactions.calls[0]
    assert call == {
        "model": "gemini-3.1-flash-lite",
        "input": "인사해줘",
        "store": False,
        "stream": True,
    }
    assert "previous_interaction_id" not in call


def test_consecutive_messages_have_no_memory() -> None:
    turn1_events = [
        {"event_type": "interaction.created", "interaction": {"id": "int_001"}},
        {"event_type": "step.delta", "delta": {"type": "text", "text": "첫 응답"}},
    ]
    turn2_events = [
        {"event_type": "interaction.created", "interaction": {"id": "int_002"}},
        {"event_type": "step.delta", "delta": {"type": "text", "text": "둘째 응답"}},
    ]
    fake_client = FakeGenAIClient([turn1_events, turn2_events])
    chat = GeminiChatClient(
        Settings(api_key="test-key", model="gemini-3.1-flash-lite"),
        client=fake_client,
    )

    assert "".join(chat.send_message_stream("내 이름은 철수야")) == "첫 응답"
    assert "".join(chat.send_message_stream("내 이름이 뭐야?")) == "둘째 응답"

    assert len(fake_client.interactions.calls) == 2
    for call in fake_client.interactions.calls:
        assert call["store"] is False
        assert call["stream"] is True
        assert "previous_interaction_id" not in call
