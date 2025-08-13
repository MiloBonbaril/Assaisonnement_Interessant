"""Text-to-speech utilities using Coqui TTS."""
from pathlib import Path
import time
from uuid import uuid4
from typing import Dict, Iterable

try:
    from TTS.api import TTS  # type: ignore
except Exception:  # pragma: no cover - handled in tests
    TTS = None  # type: ignore

try:
    from playsound import playsound  # type: ignore
except Exception:  # pragma: no cover - handled in tests
    playsound = None  # type: ignore

VOICE_MODELS: Dict[str, str] = {
    "default": "tts_models/en/ljspeech/tacotron2-DDC",
}

LOG_DIR = Path("data/audio_logs")
MAX_LOG_FILES = 3


def play_audio(path: Path) -> None:
    """Play an audio file.

    Args:
        path: Path to the WAV file.

    Raises:
        RuntimeError: If the playback library is unavailable.
    """
    if playsound is None:
        raise RuntimeError("playsound library is not installed.")
    playsound(str(path))


def _prune_logs(files: Iterable[Path]) -> None:
    """Remove old audio log files, keeping only the most recent ones."""
    for old in files:
        old.unlink()


def synthesize(text: str, voice: str) -> Path:
    """Synthesize speech from text and play it.

    Args:
        text: The text to convert to speech.
        voice: The identifier of the voice to use.

    Returns:
        Path to the generated WAV file saved in the log directory.

    Raises:
        ValueError: If the text is empty or the voice is unknown.
        RuntimeError: If the TTS or playback library is unavailable.
    """
    if not text.strip():
        raise ValueError("Text must not be empty.")
    if voice not in VOICE_MODELS:
        raise ValueError(f"Unknown voice: {voice}")
    if TTS is None:
        raise RuntimeError("Coqui TTS library is not installed.")
    # Clean the text string to avoid issues with special characters, remove emojis, etc.
    try:
        text = text.encode("ascii", "ignore").decode("ascii").strip()
    except Exception as e:
        raise ValueError(f"Error cleaning text: {e}")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time() * 1000)
    file_path = LOG_DIR / f"{timestamp}_{uuid4().hex}.wav"
    tts = TTS(VOICE_MODELS[voice])
    tts.tts_to_file(text=text, file_path=str(file_path))
    play_audio(file_path)
    files = sorted(
        LOG_DIR.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    _prune_logs(files[MAX_LOG_FILES:])
    return file_path
