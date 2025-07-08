# Assistant Virtuel - Phase 1
## Documentation Technique Complète

### 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Utilisation](#utilisation)
5. [Configuration](#configuration)
6. [API Reference](#api-reference)
7. [Développement](#développement)
8. [Tests](#tests)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Vue d'ensemble

L'Assistant Virtuel Phase 1 implémente un système conversationnel modulaire avec :

- **Personas modulables** : Assistants avec personnalités distinctes
- **Mémoire intelligente** : Court et long terme avec RAG
- **Tools extensibles** : Modules pour domotique, calendrier, météo
- **Conscience temporelle** : Adaptation selon l'heure/jour
- **Interface CLI** : Commandes intuitives et session interactive

### 🎯 Objectifs de la Phase 1

✅ **Accomplis**
- Gestion complète des personas (CRUD)
- Système de mémoire avec RAG (FAISS + embeddings)
- Architecture modulaire de tools
- Conscience temporelle (matin/après-midi/soir)
- Interface CLI riche avec Typer + Rich
- Intégration Ollama pour LLM local
- Tests unitaires et d'intégration

---

## 🏗️ Architecture

### Composants principaux

```
┌─────────────────────────────────────────────────────────────┐
│                    VirtualAssistant                         │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│ │   Persona   │ │   Memory    │ │    Tools    │ │  Time   │ │
│ │  Manager    │ │  Manager    │ │   Manager   │ │ Manager │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   OllamaClient                              │
├─────────────────────────────────────────────────────────────┤
│                      CLI Interface                          │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Système de Mémoire

#### Mémoire Court Terme
- **Session Memory** : Historique des 20 derniers échanges
- **Context Window** : 10 derniers messages pour le LLM
- **Auto-clearing** : Nettoyage automatique entre sessions

#### Mémoire Long Terme
- **Vector Store** : Index FAISS avec embeddings Sentence-BERT
- **Document Store** : SQLite pour métadonnées et contenu
- **RAG Pipeline** : Recherche sémantique + génération contextuelle

```python
# Exemple de recherche RAG
memories = memory_manager.search_memories("domotique lumière", top_k=3)
# Retourne les 3 souvenirs les plus pertinents
```

### 🎭 Système de Personas

#### Structure Persona
```python
@dataclass
class Persona:
    name: str              # Nom de la persona
    description: str       # Description du caractère
    tone: str             # Ton de communication
    reactions: List[str]  # Réactions typiques
    preferences: Dict     # Préférences personnalisées
    voice_settings: Dict  # Paramètres vocaux (Phase 2)
```

#### Personas par défaut
- **Alice** : Bienveillante et empathique
- **Bob** : Technique et précis

### 🛠️ Système de Tools

#### Interface Tool
```python
class Tool(ABC):
    @abstractmethod
    def get_name(self) -> str: pass
    
    @abstractmethod
    def get_description(self) -> str: pass
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any: pass
```

#### Tools implémentés
- **WeatherTool** : Informations météorologiques
- **CalendarTool** : Gestion RDV et rappels
- **DomoticsTool** : Contrôle équipements connectés

### ⏰ Conscience Temporelle

#### Périodes de la journée
- **Matin** : 06:00 - 12:00
- **Après-midi** : 12:00 - 18:00
- **Soir** : 18:00 - 24:00
- **Nuit** : 00:00 - 06:00

#### Contexte temporel
```python
{
    "datetime": "2024-01-15T14:30:00",
    "date": "2024-01-15",
    "time": "14:30:00",
    "period": "après-midi",
    "day_name": "Lundi",
    "month_name": "Janvier"
}
```

---

## 🚀 Installation

### Prérequis
- **Python 3.13+**
- **Ollama** (pour LLM local)
- **Git**

### Installation automatique
```bash
git clone https://github.com/votre-repo/va-assistant.git
cd va-assistant
chmod +x install.sh
./install.sh
```

### Installation manuelle
```bash
# Clone du projet
git clone https://github.com/votre-repo/va-assistant.git
cd va-assistant

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installation des dépendances
pip install -r requirements.txt
pip install -e .

# Installation d'Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:latest
```

### Installation avec Docker
```bash
# Lancement avec Docker Compose
docker-compose up -d

# Utilisation
docker-compose exec va-assistant va start
```

---

## 💻 Utilisation

### Commandes CLI

#### Démarrer une session interactive
```bash
va start
```

#### Poser une question directe
```bash
va ask "Quelle heure est-il ?"
va ask "Allume la lumière du salon"
```

#### Gestion des personas
```bash
# Changer de persona
va switch --persona alice
va switch --persona bob

# Lister les personas
va list-personas
```

#### Gestion des tools
```bash
# Lister les tools disponibles
va list-tools
```

#### Informations système
```bash
# Informations temporelles
va time-info

# Statistiques mémoire
va memory-stats
```

### Session Interactive

```bash
$ va start
╭─────────────────────────────────────────────────────────╮
│           Assistant Virtuel - Session Interactive       │
╰─────────────────────────────────────────────────────────╯
Persona active: Alice
Tapez 'quit' pour quitter

Vous: Bonjour Alice, comment allez-vous ?
Alice: Bonjour ! Je vais très bien, merci de demander. 
Comment puis-je vous aider aujourd'hui ?

Vous: Quelle heure est-il ?
Alice: Il est actuellement 14:30. Nous sommes en 
début d'après-midi, un bon moment pour être productif !

Vous: quit
Session terminée
```

---

## ⚙️ Configuration

### Fichier de configuration
Le système utilise une configuration par défaut modifiable :

```python
CONFIG = {
    "data_dir": Path.home() / ".va_assistant",
    "personas_file": "personas.json",
    "memory_db": "memory.db",
    "vector_index": "memory_vectors.index",
    "ollama_url": "http://localhost:11434",
    "timezone": "Europe/Paris"
}
```

### Structure des données
```
~/.va_assistant/
├── personas.json           # Définitions des personas
├── memory.db              # Base de données mémoire
├── memory_vectors.index   # Index vectoriel FAISS
└── logs/                  # Logs système
```

### Personas personnalisées
Créez vos propres personas en éditant `personas.json` :

```json
{
  "expert_tech": {
    "name": "TechExpert",
    "description": "Expert technique spécialisé",
    "tone": "précis et technique",
    "reactions": ["analytique", "méthodique", "détaillé"],
    "preferences": {
      "communication": "technique",
      "détails": "maximum",
      "exemples": "code"
    }
  }
}
```

---

## 📚 API Reference

### PersonaManager

#### Méthodes principales
```python
# Charger une persona
persona = persona_manager.get_persona("alice")

# Ajouter une persona
new_persona = Persona(name="Charlie", ...)
persona_manager.add_persona(new_persona)

# Supprimer une persona
persona_manager.remove_persona("charlie")

# Lister les personas
personas = persona_manager.list_personas()
```

### MemoryManager

#### Gestion mémoire court terme
```python
# Ajouter à la session
memory_manager.add_to_session("Message utilisateur", "user")
memory_manager.add_to_session("Réponse assistant", "assistant")

# Récupérer le contexte
context = memory_manager.get_session_context()
```

#### Gestion mémoire long terme
```python
# Ajouter à la mémoire long terme
memory_id = memory_manager.add_to_long_term(
    content="Information importante",
    memory_type="conversation",
    metadata={"topic": "domotique"}
)

# Rechercher dans la mémoire
results = memory_manager.search_memories("domotique", top_k=5)
```

### ToolManager

#### Enregistrement de tools
```python
# Créer un tool personnalisé
class CustomTool(Tool):
    def get_name(self) -> str:
        return "custom_tool"
    
    def get_description(self) -> str:
        return "Mon tool personnalisé"
    
    async def run(self, *args, **kwargs) -> Any:
        return {"result": "success"}

# Enregistrer le tool
tool_manager.register_tool(CustomTool())

# Utiliser le tool
result = await tool_manager.run_tool("custom_tool", param="value")
```

### TimeManager

#### Utilisation
```python
# Heure actuelle
current_time = time_manager.get_current_time()

# Période de la journée
period = time_manager.get_time_period()  # "matin", "après-midi", "soir", "nuit"

# Contexte complet
context = time_manager.get_temporal_context()
```

---

## 🔧 Développement

### Structure du projet
```
va-assistant/
├── va_assistant/
│   ├── __init__.py
│   ├── main.py              # Code principal
│   ├── models/              # Modèles de données
│   ├── managers/            # Gestionnaires
│   ├── tools/               # Tools disponibles
│   └── utils/               # Utilitaires
├── tests/                   # Tests unitaires
├── docs/                    # Documentation
├── requirements.txt         # Dépendances
├── setup.py                 # Configuration package
├── Dockerfile              # Configuration Docker
└── docker-compose.yml      # Orchestration
```

### Développer un nouveau tool

1. **Créer la classe Tool**
```python
from va_assistant.tools.base import Tool

class MyTool(Tool):
    def get_name(self) -> str:
        return "my_tool"
    
    def get_description(self) -> str:
        return "Description de mon tool"
    
    async def run(self, action: str, **kwargs) -> Dict:
        if action == "test":
            return {"status": "success", "message": "Test OK"}
        return {"status": "error", "message": "Action inconnue"}
```

2. **Enregistrer le tool**
```python
# Dans main.py ou un module d'initialisation
tool_manager.register_tool(MyTool())
```

3. **Utiliser le tool**
```python
# L'assistant peut maintenant utiliser votre tool
result = await tool_manager.run_tool("my_tool", action="test")
```

### Développer une nouvelle persona

1. **Définir la persona**
```python
expert_persona = Persona(
    name="Expert",
    description="Spécialiste dans un domaine",
    tone="professionnel et précis",
    reactions=["analytique", "méthodique"],
    preferences={
        "style": "technique",
        "exemples": "détaillés",
        "format": "structuré"
    }
)
```

2. **Ajouter au système**
```python
persona_manager.add_persona(expert_persona)
```

### Hooks de développement

#### Pre-commit hooks
```bash
# Installation
pip install pre-commit
pre-commit install

# Configuration dans .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## 🧪 Tests

### Exécution des tests
```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_personas.py -v
pytest tests/test_memory.py -v

# Tests avec couverture
pytest tests/ --cov=va_assistant --cov-report=html
```

### Types de tests

#### Tests unitaires
```python
def test_persona_creation():
    persona = Persona(
        name="Test",
        description="Test persona",
        tone="test",
        reactions=["calm"],
        preferences={"test": "value"}
    )
    assert persona.name == "Test"
```

#### Tests d'intégration
```python
def test_full_conversation_flow():
    assistant = VirtualAssistant()
    assistant.load_persona("alice")
    response = assistant.process_query("Bonjour")
    assert response is not None
```

#### Tests de performance
```bash
# Mesure du temps de réponse
pytest tests/test_performance.py --benchmark-only
```

---

## 🔍 Troubleshooting

### Problèmes courants

#### Ollama non disponible
```bash
# Vérifier le statut
curl http://localhost:11434/api/version

# Redémarrer Ollama
ollama serve

# Vérifier les modèles
ollama list
```

#### Erreurs de mémoire
```bash
# Vérifier les statistiques
va memory-stats

# Nettoyer la mémoire
rm ~/.va_assistant/memory.db
rm ~/.va_assistant/memory_vectors.index
```

#### Problèmes de personas
```bash
# Réinitialiser les personas
rm ~/.va_assistant/personas.json
va list-personas  # Recrée les personas par défaut
```

#### Erreurs de dépendances
```bash
# Réinstaller l'environnement
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Logs de debug

#### Activer les logs détaillés
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Localisation des logs
```bash
# Logs système
tail -f ~/.va_assistant/logs/va_assistant.log

# Logs Ollama
tail -f ~/.ollama/logs/server.log
```

### Support et communauté

- **Issues GitHub** : [github.com/votre-repo/va-assistant/issues](https://github.com/votre-repo/va-assistant/issues)
- **Discussions** : [github.com/votre-repo/va-assistant/discussions](https://github.com/votre-repo/va-assistant/discussions)
- **Wiki** : [github.com/votre-repo/va-assistant/wiki](https://github.com/votre-repo/va-assistant/wiki)

---

## 📈 Métriques et Performance

### Critères de succès Phase 1

- ✅ **Temps de réponse** : < 1s pour requêtes textuelles
- ✅ **Modularité** : Ajout/suppression sans redéploiement
- ✅ **Précision mémoire** : > 80% de rappels pertinents
- ✅ **Stabilité** : 99% uptime en usage normal

### Monitoring

```bash
# Statistiques en temps réel
va memory-stats
va time-info

# Métriques système
top -p $(pgrep -f "va start")
```

---

## 🚀 Roadmap Phase 2

### Fonctionnalités prévues

- **Synthèse vocale** : TTS avec voix modulables
- **Reconnaissance vocale** : STT pour interactions orales
- **Computer Vision** : Analyse d'images et vidéos
- **Pipeline audio** : Sessions vocales continues
- **Transcription média** : Ingestion épisodes séries/films

### Architecture évolutive

L'architecture actuelle est conçue pour supporter les extensions Phase 2 :

- **Interfaces modulaires** : Ajout facile de nouveaux types d'entrée
- **Gestion asynchrone** : Prêt pour les pipelines audio/vidéo
- **Extensibilité tools** : Framework pour nouveaux modules
- **Mémoire évolutive** : Support multimédia intégré

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🙏 Remerciements

- **Ollama** : Pour l'infrastructure LLM locale
- **Sentence Transformers** : Pour les embeddings sémantiques
- **FAISS** : Pour l'indexation vectorielle performante
- **Typer & Rich** : Pour l'interface CLI élégante

---

*Documentation générée automatiquement - Version 1.0.0*
