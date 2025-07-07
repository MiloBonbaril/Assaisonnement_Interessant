# tests/test_va_assistant.py
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Import des classes à tester
from va_assistant.main import (
    Persona, PersonaManager, MemoryManager, 
    ToolManager, TimeManager, VirtualAssistant
)

class TestPersona:
    def test_persona_creation(self):
        persona = Persona(
            name="Test",
            description="Test persona",
            tone="test",
            reactions=["calm"],
            preferences={"test": "value"}
        )
        assert persona.name == "Test"
        assert persona.description == "Test persona"
        assert persona.tone == "test"
        assert persona.reactions == ["calm"]
        assert persona.preferences == {"test": "value"}
    
    def test_persona_serialization(self):
        persona = Persona(
            name="Test",
            description="Test persona",
            tone="test",
            reactions=["calm"],
            preferences={"test": "value"}
        )
        
        # Test to_dict
        data = persona.to_dict()
        assert data["name"] == "Test"
        assert data["description"] == "Test persona"
        
        # Test from_dict
        restored = Persona.from_dict(data)
        assert restored.name == persona.name
        assert restored.description == persona.description
        assert restored.tone == persona.tone
        assert restored.reactions == persona.reactions
        assert restored.preferences == persona.preferences

class TestPersonaManager:
    def test_persona_manager_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock du CONFIG
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'personas_file': 'personas.json'}):
                manager = PersonaManager()
                assert len(manager.personas) == 2  # Alice et Bob par défaut
                assert "alice" in manager.personas
                assert "bob" in manager.personas
    
    def test_add_persona(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'personas_file': 'personas.json'}):
                manager = PersonaManager()
                
                new_persona = Persona(
                    name="Charlie",
                    description="Test persona",
                    tone="friendly",
                    reactions=["helpful"],
                    preferences={"style": "casual"}
                )
                
                result = manager.add_persona(new_persona)
                assert result == True
                assert "charlie" in manager.personas
                assert manager.get_persona("charlie") is not None
    
    def test_remove_persona(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'personas_file': 'personas.json'}):
                manager = PersonaManager()
                
                # Ajouter une persona
                new_persona = Persona(
                    name="ToDelete",
                    description="Test",
                    tone="test",
                    reactions=["test"],
                    preferences={}
                )
                manager.add_persona(new_persona)
                
                # Supprimer la persona
                result = manager.remove_persona("ToDelete")
                assert result == True
                assert "todelete" not in manager.personas

class TestMemoryManager:
    def test_memory_manager_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'memory_db': 'memory.db', 'vector_index': 'vectors.index'}):
                manager = MemoryManager()
                assert manager.session_memory == []
                assert manager.index is not None
    
    def test_session_memory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'memory_db': 'memory.db', 'vector_index': 'vectors.index'}):
                manager = MemoryManager()
                
                manager.add_to_session("Test message", "user")
                assert len(manager.session_memory) == 1
                assert manager.session_memory[0]["content"] == "Test message"
                assert manager.session_memory[0]["role"] == "user"
    
    def test_session_memory_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'memory_db': 'memory.db', 'vector_index': 'vectors.index'}):
                manager = MemoryManager()
                
                # Ajouter plus de 20 messages
                for i in range(25):
                    manager.add_to_session(f"Message {i}", "user")
                
                # Vérifier que seuls les 20 derniers sont conservés
                assert len(manager.session_memory) == 20
                assert manager.session_memory[0]["content"] == "Message 5"
                assert manager.session_memory[-1]["content"] == "Message 24"

class TestToolManager:
    def test_tool_manager_creation(self):
        manager = ToolManager()
        assert len(manager.tools) == 3  # weather, calendar, domotics
        assert "weather" in manager.tools
        assert "calendar" in manager.tools
        assert "domotics" in manager.tools
    
    def test_tool_registration(self):
        manager = ToolManager()
        
        # Mock tool
        mock_tool = Mock()
        mock_tool.get_name.return_value = "test_tool"
        mock_tool.get_description.return_value = "Test tool"
        
        manager.register_tool(mock_tool)
        assert "test_tool" in manager.tools
        assert manager.get_tool("test_tool") == mock_tool
    
    def test_tool_unregistration(self):
        manager = ToolManager()
        
        # Tester la suppression d'un tool existant
        result = manager.unregister_tool("weather")
        assert result == True
        assert "weather" not in manager.tools
        
        # Tester la suppression d'un tool inexistant
        result = manager.unregister_tool("nonexistent")
        assert result == False

class TestTimeManager:
    def test_time_manager_creation(self):
        manager = TimeManager()
        assert manager.timezone == "Europe/Paris"
    
    def test_time_periods(self):
        manager = TimeManager()
        
        # Mock datetime pour tester les périodes
        with patch('va_assistant.main.datetime') as mock_datetime:
            # Test matin
            mock_datetime.now.return_value.time.return_value = Mock()
            mock_datetime.now.return_value.time.return_value.__lt__ = lambda self, other: True
            mock_datetime.now.return_value.time.return_value.__ge__ = lambda self, other: True
            
            # Les tests spécifiques des périodes nécessiteraient une configuration plus complexe
            # Pour l'instant, on teste juste que la méthode fonctionne
            period = manager.get_time_period()
            assert period in ["matin", "après-midi", "soir", "nuit"]
    
    def test_temporal_context(self):
        manager = TimeManager()
        context = manager.get_temporal_context()
        
        assert "datetime" in context
        assert "date" in context
        assert "time" in context
        assert "period" in context
        assert "day_name" in context
        assert "month_name" in context

class TestVirtualAssistant:
    def test_virtual_assistant_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'personas_file': 'personas.json', 'memory_db': 'memory.db', 'vector_index': 'vectors.index'}):
                assistant = VirtualAssistant()
                assert assistant.persona_manager is not None
                assert assistant.memory_manager is not None
                assert assistant.tool_manager is not None
                assert assistant.time_manager is not None
                assert assistant.ollama_client is not None
                assert assistant.current_persona is None
                assert assistant.session_active == False
    
    def test_load_persona(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('va_assistant.main.CONFIG', {'data_dir': Path(tmpdir), 'personas_file': 'personas.json', 'memory_db': 'memory.db', 'vector_index': 'vectors.index'}):
                assistant = VirtualAssistant()
                
                # Charger une persona existante
                result = assistant.load_persona("alice")
                assert result == True
                assert assistant.current_persona is not None
                assert assistant.current_persona.name == "Alice"
                
                # Charger une persona inexistante
                result = assistant.load_persona("nonexistent")
                assert result == False

# Configuration pytest
def pytest_configure(config):
    """Configuration globale des tests"""
    pass

# Fixtures
@pytest.fixture
def temp_config():
    """Fixture pour configuration temporaire"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'data_dir': Path(tmpdir),
            'personas_file': 'personas.json',
            'memory_db': 'memory.db',
            'vector_index': 'vectors.index',
            'ollama_url': 'http://localhost:11434',
            'timezone': 'Europe/Paris'
        }
        yield config

@pytest.fixture
def mock_ollama_response():
    """Fixture pour réponse Ollama mockée"""
    return {
        "message": {
            "content": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        }
    }

# Tests d'intégration
class TestIntegration:
    def test_full_conversation_flow(self, temp_config, mock_ollama_response):
        """Test du flux complet de conversation"""
        with patch('va_assistant.main.CONFIG', temp_config):
            with patch('requests.post') as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = mock_ollama_response
                
                assistant = VirtualAssistant()
                assistant.load_persona("alice")
                
                # Simuler une conversation
                response = assistant.process_query("Bonjour")
                # Le test devrait passer même si Ollama n'est pas disponible
                assert response is not None
