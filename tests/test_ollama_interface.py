import pytest
from unittest.mock import patch, MagicMock
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

def test_debug_prints_generate_response(sample_messages, capsys):
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = {"message": {"content": "foo"}}
        oi = OllamaInterface("test-model", debug=True)
        oi.generate_response(messages=sample_messages)
        captured = capsys.readouterr()
        assert "Generating response for prompt" in captured.out

def test_debug_prints_stream_response(sample_messages, capsys):
    fake_stream = [{"message": {"content": "foo"}}]
    with patch("src.ollama_interface.ollama.chat") as mock_chat:
        mock_chat.return_value = iter(fake_stream)
        oi = OllamaInterface("test-model", debug=True)
        list(oi.stream_response(messages=sample_messages))
        captured = capsys.readouterr()
        assert "Streaming response for prompt" in captured.out
