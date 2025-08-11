"""Tests for the text-to-speech engine."""
from pathlib import Path
from unittest.mock import patch
import time

import pytest

from src import tts_engine


def _fake_tts_to_file(text: str, file_path: str) -> None:
    Path(file_path).write_bytes(b"audio")


def test_synthesize_creates_file_and_plays_audio(tmp_path) -> None:
    with (
        patch.object(tts_engine, "TTS") as mock_tts,
        patch.object(tts_engine, "play_audio") as mock_play,
        patch.object(tts_engine, "LOG_DIR", tmp_path),
    ):
        mock_tts.return_value.tts_to_file.side_effect = _fake_tts_to_file
        path = tts_engine.synthesize("hello", "default")
        assert path.exists()
        mock_play.assert_called_once_with(path)


def test_synthesize_keeps_last_three_files(tmp_path) -> None:
    with (
        patch.object(tts_engine, "TTS") as mock_tts,
        patch.object(tts_engine, "play_audio"),
        patch.object(tts_engine, "LOG_DIR", tmp_path),
    ):
        mock_tts.return_value.tts_to_file.side_effect = _fake_tts_to_file
        paths = []
        for i in range(4):
            paths.append(tts_engine.synthesize(f"hi {i}", "default"))
            time.sleep(0.01)
        remaining = list(tmp_path.glob("*.wav"))
        assert len(remaining) == 3
        assert paths[0] not in remaining
        for path in paths[1:]:
            assert path in remaining


def test_unknown_voice_raises() -> None:
    with pytest.raises(ValueError):
        tts_engine.synthesize("hello", "unknown")


def test_empty_text_raises() -> None:
    with pytest.raises(ValueError):
        tts_engine.synthesize("", "default")

