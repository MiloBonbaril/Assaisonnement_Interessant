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

def test_debug_prints(caplog):
    persona = DummyPersona(name="Lilly", mood_tags=["cheerful"], tone="friendly", guidelines=[], limitations=[], greetings=[])
    pm = PromptManager(persona, debug=True)
    import logging
    logger_name = "PromptManager"
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        pm.get_system_prompt()
    assert any("System prompt generated" in message for message in caplog.text.splitlines())


class DummyTool:
    def get_tool_prompt(self):
        return "tool prompt"


def test_tool_prompt_included():
    persona = DummyPersona(name="Lilly", mood_tags=["cheerful"], tone="", guidelines=[], limitations=[], greetings=[])
    pm = PromptManager(persona, tools=[DummyTool()])
    prompt = pm.get_system_prompt()["content"]
    assert "tool prompt" in prompt


def test_no_limitations_section_when_empty():
    persona = DummyPersona(name="Lilly", mood_tags=["cheerful"], tone="friendly", guidelines=["Be kind"], limitations=[], greetings=[])
    pm = PromptManager(persona)
    prompt = pm.get_system_prompt()["content"]
    assert "Your limitations are:" not in prompt
