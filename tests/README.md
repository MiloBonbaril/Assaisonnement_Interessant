# Tests de l'Assistant Virtuel - Phase 1

## Exécution des tests

### Tous les tests
```bash
pytest tests/ -v
```

### Tests spécifiques
```bash
pytest tests/test_va_assistant.py::TestPersona -v
pytest tests/test_va_assistant.py::TestMemoryManager -v
```

### Tests avec couverture
```bash
pytest tests/ --cov=va_assistant --cov-report=html
```

## Structure des tests

- `TestPersona`: Tests de la classe Persona
- `TestPersonaManager`: Tests du gestionnaire de personas
- `TestMemoryManager`: Tests du système de mémoire
- `TestToolManager`: Tests du gestionnaire de tools
- `TestTimeManager`: Tests de la conscience temporelle
- `TestVirtualAssistant`: Tests de l'assistant principal
- `TestIntegration`: Tests d'intégration

## Prérequis

- Python 3.13+
- pytest
- pytest-cov (pour la couverture)
- pytest-asyncio (pour les tests asynchrones)

## Installation des dépendances de test

```bash
pip install pytest pytest-cov pytest-asyncio
```

## Mocking

Les tests utilisent des mocks pour :
- Le système de fichiers (tempfile)
- Les appels HTTP (requests)
- Les composants système (datetime)
- Ollama (pour éviter les dépendances externes)

## Fixtures

- `temp_config`: Configuration temporaire pour les tests
- `mock_ollama_response`: Réponse Ollama mockée