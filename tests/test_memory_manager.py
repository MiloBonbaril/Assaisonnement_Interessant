import os
import json
import tempfile
import pytest
from src.memory_manager import MemoryManager

@pytest.fixture
def temp_memory_file():
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_create_and_is_new_memory(temp_memory_file):
    mm = MemoryManager(temp_memory_file, debug=True)
    assert mm.is_new_memory is True
    assert os.path.exists(temp_memory_file)
    assert mm.get_memory() == []

def test_add_and_get_memory_entry(temp_memory_file):
    mm = MemoryManager(temp_memory_file)
    mm.add_memory_entry({"role": "system", "content": "hello"})
    mem = mm.get_memory()
    assert len(mem) == 1
    assert mem[0]["role"] == "system"
    assert mem[0]["content"] == "hello"

def test_add_memory_entry_list(temp_memory_file):
    mm = MemoryManager(temp_memory_file)
    entries = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"}
    ]
    mm.add_memory_entry(entries)
    mem = mm.get_memory()
    assert mem == entries

def test_save_and_load_memory(temp_memory_file):
    mm = MemoryManager(temp_memory_file)
    mm.add_memory_entry({"role": "system", "content": "persist"})
    mm2 = MemoryManager(temp_memory_file)
    assert mm2.get_memory()[0]["content"] == "persist"

def test_clear_memory(temp_memory_file):
    mm = MemoryManager(temp_memory_file)
    mm.add_memory_entry({"role": "system", "content": "to be cleared"})
    mm.clear_memory()
    assert mm.get_memory() == []

def test_invalid_json_file(tmp_path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("not a json")
    mm = MemoryManager(str(file_path))
    assert mm.get_memory() == []

def test_memory_file_extension(tmp_path):
    file_path = tmp_path / "memoryfile"
    mm = MemoryManager(str(file_path))
    assert mm.memory_file.endswith('.json')
