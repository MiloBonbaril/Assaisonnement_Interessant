import os
import json
import tempfile
import sys
import types
import pytest

# Create lightweight stubs for heavy optional dependencies
fake_np = types.SimpleNamespace(array=lambda x, dtype=None: x)

class DummyIndex:
    def __init__(self, dims):
        self.vectors = []

    def add(self, vecs):
        self.vectors.extend(vecs)

    def search(self, vecs, top_k):
        return [[0.0] * top_k], [[0] * top_k]


def write_index(index, path):
    open(path, 'wb').close()


def read_index(path):
    return DummyIndex(384)


fake_faiss = types.SimpleNamespace(
    IndexFlatL2=DummyIndex, write_index=write_index, read_index=read_index
)
fake_ollama = types.SimpleNamespace(chat=lambda *args, **kwargs: None)
sys.modules.setdefault('numpy', fake_np)
sys.modules.setdefault('faiss', fake_faiss)
sys.modules.setdefault('ollama', fake_ollama)

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
    assert os.path.exists(mm.rag_db_path)

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


def test_token_count(temp_memory_file):
    mm = MemoryManager(temp_memory_file)
    mm.add_memory_entry({"role": "user", "content": "hello world"})
    mm.add_memory_entry({"role": "assistant", "content": "hi there"})
    assert mm.get_token_count() == 4


def test_empty_memory_file_raises():
    with pytest.raises(ValueError):
        MemoryManager("")


def test_tool_memory_integration(temp_memory_file):
    class DummyTool:
        def get_tool_memory(self):
            return "tool memory"

    mm = MemoryManager(temp_memory_file, tools=[DummyTool()])
    mm.add_memory_entry({"role": "user", "content": "hi"})
    mem = mm.get_memory()
    assert mem[0]["content"] == "tool memory"
    assert mem[1]["content"] == "hi"


def test_get_memory_reload(temp_memory_file):
    mm = MemoryManager(temp_memory_file)
    mm.add_memory_entry({"role": "system", "content": "persist"})
    mm.memory = []
    reloaded = mm.get_memory()
    assert reloaded == [{"role": "system", "content": "persist"}]
