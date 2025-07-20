import pytest
from src.prompt_manager import PromptManager

class DummyPersona:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def test_system_prompt_full():
    persona = DummyPersona(
        name="Lilly",
        mood_tags=["cheerful", "curious"],
        tone="friendly",
        guidelines=["Be helpful", "Be concise"],
        limitations=["Don't give medical advice"],
        greetings=["Hi!", "Hello!"]
    )
    pm = PromptManager(persona)
    prompt = pm.get_system_prompt()
    content = prompt["content"]
    assert "You are Lilly, a cheerful, curious assistant." in content
    assert "Your tone is: friendly." in content
    assert "- Be helpful" in content
    assert "- Be concise" in content
    assert "- Don't give medical advice" in content
    assert 'Sample greetings: "Hi!", "Hello!"' in content

def test_system_prompt_minimal():
    persona = DummyPersona(name="Lilly", mood_tags=[], tone="", guidelines=[], limitations=[], greetings=[])
    pm = PromptManager(persona)
    prompt = pm.get_system_prompt()
    assert "You are Lilly, an assistant." in prompt["content"]

def test_system_prompt_no_name():
    persona = DummyPersona(name="", mood_tags=["cheerful"], tone="", guidelines=[], limitations=[], greetings=[])
    pm = PromptManager(persona)
    prompt = pm.get_system_prompt()
    assert "You are" not in prompt["content"]

def test_debug_prints(capsys):
    persona = DummyPersona(name="Lilly", mood_tags=["cheerful"], tone="friendly", guidelines=[], limitations=[], greetings=[])
    pm = PromptManager(persona, debug=True)
    pm.get_system_prompt()
    captured = capsys.readouterr()
    assert "System prompt generated" in captured.out
