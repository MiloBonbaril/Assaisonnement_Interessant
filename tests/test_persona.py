import os
import json
import tempfile
import pytest
from src.persona import Persona

@pytest.fixture
def persona_json(tmp_path):
    data = {
        "name": "Lilly",
        "mood_tags": ["cheerful", "curious"],
        "behavior": {
            "greeting": ["Hi!", "Hello!"],
            "tone": "friendly",
            "guidelines": ["Be helpful"],
            "limitations": ["Don't give medical advice"]
        }
    }
    file_path = tmp_path / "persona.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return str(file_path), data

def test_load_persona_file_direct(persona_json):
    file_path, data = persona_json
    p = Persona(file_path)
    assert p.name == data["name"]
    assert p.mood_tags == data["mood_tags"]
    assert p.greetings == data["behavior"]["greeting"]
    assert p.tone == data["behavior"]["tone"]
    assert p.guidelines == data["behavior"]["guidelines"]
    assert p.limitations == data["behavior"]["limitations"]

def test_load_persona_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        Persona(str(tmp_path / "notfound.json"))

def test_invalid_json(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("not a json")
    with pytest.raises(ValueError):
        Persona(str(file_path))

def test_str_method(persona_json):
    file_path, data = persona_json
    p = Persona(file_path)
    s = str(p)
    assert "Persona(name=Lilly" in s
    assert "cheerful" in s
