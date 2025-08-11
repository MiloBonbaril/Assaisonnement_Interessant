import sys
import types
import pytest
from unittest.mock import patch, MagicMock

# Provide a minimal stub for the external ollama package
fake_ollama = types.SimpleNamespace(chat=lambda *args, **kwargs: None)
sys.modules.setdefault('ollama', fake_ollama)

from src.ollama_interface import OllamaInterface

@pytest.fixture
def sample_messages():
    return [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi!"}
    ]

def test_generate_response_calls_ollama_chat(sample_messages):
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = {"message": {"content": "response text"}}
        oi = OllamaInterface("test-model", debug=True)
        result = oi.generate_response(messages=sample_messages, think=True)
        mock_chat.assert_called_once_with(model="test-model", messages=sample_messages, think=True)
        assert result == "response text"

def test_stream_response_yields_chunks(sample_messages):
    fake_stream = [
        {"message": {"content": "part1"}},
        {"message": {"content": "part2"}}
    ]
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = iter(fake_stream)
        oi = OllamaInterface("test-model")
        chunks = list(oi.stream_response(messages=sample_messages, think=False))
        mock_chat.assert_called_once_with(model="test-model", messages=sample_messages, stream=True, think=False)
        assert chunks == ["part1", "part2"]

def test_debug_prints_generate_response(sample_messages, caplog):
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = {"message": {"content": "foo"}}
        oi = OllamaInterface("test-model", debug=True)
        import logging
        logger_name = "OllamaInterface"
        with caplog.at_level(logging.DEBUG, logger=logger_name):
            oi.generate_response(messages=sample_messages)
        assert any("Generating response for prompt" in message for message in caplog.text.splitlines())

def test_debug_prints_stream_response(sample_messages, caplog):
    fake_stream = [{"message": {"content": "foo"}}]
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = iter(fake_stream)
        oi = OllamaInterface("test-model", debug=True)
        import logging
        logger_name = "OllamaInterface"
        with caplog.at_level(logging.DEBUG, logger=logger_name):
            list(oi.stream_response(messages=sample_messages))
        assert any("Streaming response for prompt" in message for message in caplog.text.splitlines())


def test_default_think_false(sample_messages):
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = {"message": {"content": "text"}}
        oi = OllamaInterface("test-model")
        oi.generate_response(messages=sample_messages)
        mock_chat.assert_called_once_with(model="test-model", messages=sample_messages, think=False)


def test_retry_on_failure(sample_messages):
    side_effects = [Exception("boom"), Exception("boom"), {"message": {"content": "ok"}}]
    with patch("src.ollama_interface.ollama.chat", side_effect=side_effects) as mock_chat:
        oi = OllamaInterface("test-model")
        result = oi.generate_response(messages=sample_messages)
        assert result == "ok"
        assert mock_chat.call_count == 3


def test_raises_after_max_attempts(sample_messages):
    with patch("src.ollama_interface.ollama.chat", side_effect=RuntimeError("fail")):
        oi = OllamaInterface("test-model")
        with pytest.raises(RuntimeError):
            oi.generate_response(messages=sample_messages)
