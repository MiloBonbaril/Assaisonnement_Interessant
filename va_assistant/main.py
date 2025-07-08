# Assistant Virtuel - Phase 1
# Architecture complète avec CLI, Persona, Tools et Mémoire

import json
import os
import sqlite3
import asyncio
from datetime import datetime, time
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass, asdict
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import requests
from abc import ABC, abstractmethod

# Configuration
console = Console()
app = typer.Typer()

# Configuration globale
CONFIG = {
    "data_dir": Path.home() / ".va_assistant",
    "personas_file": "personas.json",
    "memory_db": "memory.db",
    "vector_index": "memory_vectors.index",
    "ollama_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
    "timezone": "Europe/Paris"
}

# Création du répertoire de données
CONFIG["data_dir"].mkdir(exist_ok=True)

# =============================================================================
# GESTION DES PERSONAS
# =============================================================================

@dataclass
class Persona:
    """Classe représentant une persona"""
    name: str
    description: str
    tone: str
    reactions: List[str]
    preferences: Dict[str, Any]
    voice_settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Persona':
        return cls(**data)

class PersonaManager:
    """Gestionnaire des personas"""
    
    def __init__(self):
        self.personas_file = CONFIG["data_dir"] / CONFIG["personas_file"]
        self.personas: Dict[str, Persona] = {}
        self.load_personas()
    
    def load_personas(self):
        """Charge les personas depuis le fichier JSON"""
        if self.personas_file.exists():
            try:
                with open(self.personas_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.personas = {
                        name: Persona.from_dict(persona_data)
                        for name, persona_data in data.items()
                    }
            except Exception as e:
                console.print(f"[red]Erreur lors du chargement des personas: {e}[/red]")
        else:
            # Création de personas par défaut
            self.create_default_personas()
    
    def save_personas(self):
        """Sauvegarde les personas dans le fichier JSON"""
        try:
            data = {name: persona.to_dict() for name, persona in self.personas.items()}
            with open(self.personas_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            console.print(f"[red]Erreur lors de la sauvegarde: {e}[/red]")
    
    def create_default_personas(self):
        """Crée les personas par défaut"""
        alice = Persona(
            name="Alice",
            description="Assistante bienveillante et empathique",
            tone="chaleureux et professionnel",
            reactions=["encourageante", "patiente", "curieuse"],
            preferences={"communication": "claire", "humour": "léger"}
        )
        
        bob = Persona(
            name="Bob",
            description="Assistant technique et précis",
            tone="direct et factuel",
            reactions=["analytique", "efficace", "méthodique"],
            preferences={"communication": "concise", "détails": "techniques"}
        )
        
        self.personas = {"alice": alice, "bob": bob}
        self.save_personas()
    
    def get_persona(self, name: str) -> Optional[Persona]:
        """Récupère une persona par nom"""
        return self.personas.get(name.lower())
    
    def add_persona(self, persona: Persona) -> bool:
        """Ajoute une nouvelle persona"""
        try:
            self.personas[persona.name.lower()] = persona
            self.save_personas()
            return True
        except Exception as e:
            console.print(f"[red]Erreur lors de l'ajout: {e}[/red]")
            return False
    
    def remove_persona(self, name: str) -> bool:
        """Supprime une persona"""
        if name.lower() in self.personas:
            del self.personas[name.lower()]
            self.save_personas()
            return True
        return False
    
    def list_personas(self) -> List[str]:
        """Liste toutes les personas disponibles"""
        return list(self.personas.keys())

# =============================================================================
# SYSTÈME DE MÉMOIRE
# =============================================================================

class MemoryManager:
    """Gestionnaire de mémoire court et long terme"""
    
    def __init__(self):
        self.db_path = CONFIG["data_dir"] / CONFIG["memory_db"]
        self.vector_path = CONFIG["data_dir"] / CONFIG["vector_index"]
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.index = None
        self.session_memory = []  # Mémoire court terme
        self.setup_database()
        self.setup_vector_index()
    
    def setup_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT DEFAULT 'conversation',
                metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def setup_vector_index(self):
        """Initialise l'index vectoriel FAISS"""
        if self.vector_path.exists():
            self.index = faiss.read_index(str(self.vector_path))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def add_to_session(self, content: str, role: str = "user"):
        """Ajoute à la mémoire de session (court terme)"""
        self.session_memory.append({
            "content": content,
            "role": role,
            "timestamp": datetime.now()
        })
        
        # Limite la mémoire de session à 20 échanges
        if len(self.session_memory) > 20:
            self.session_memory = self.session_memory[-20:]
    
    def add_to_long_term(self, content: str, memory_type: str = "conversation", metadata: Dict = None):
        """Ajoute à la mémoire long terme avec indexation vectorielle"""
        # Stockage en base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memories (content, type, metadata)
            VALUES (?, ?, ?)
        ''', (content, memory_type, json.dumps(metadata) if metadata else None))
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Indexation vectorielle
        embedding = self.model.encode([content])
        self.index.add(embedding)
        
        # Sauvegarde de l'index
        faiss.write_index(self.index, str(self.vector_path))
        
        return memory_id
    
    def search_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recherche dans la mémoire long terme"""
        if self.index.ntotal == 0:
            return []
        
        # Recherche vectorielle
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Récupération des contenus
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM memories ORDER BY id')
        all_memories = cursor.fetchall()
        conn.close()
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(all_memories):
                memory = all_memories[idx]
                results.append({
                    "id": memory[0],
                    "content": memory[1],
                    "timestamp": memory[2],
                    "type": memory[3],
                    "metadata": json.loads(memory[4]) if memory[4] else {},
                    "distance": distances[0][i]
                })
        
        return results
    
    def get_session_context(self) -> List[Dict]:
        """Récupère le contexte de session"""
        return self.session_memory[-10:]  # 10 derniers échanges
    
    def clear_session(self):
        """Vide la mémoire de session"""
        self.session_memory = []

# =============================================================================
# SYSTÈME DE TOOLS
# =============================================================================

class Tool(ABC):
    """Interface abstraite pour les tools"""
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        pass

class WeatherTool(Tool):
    """Tool pour récupérer la météo"""
    
    def get_name(self) -> str:
        return "weather"
    
    def get_description(self) -> str:
        return "Récupère les informations météorologiques"
    
    async def run(self, location: str = "Paris") -> Dict:
        # Simulation d'appel API météo
        return {
            "location": location,
            "temperature": "22°C",
            "condition": "Ensoleillé",
            "humidity": "65%"
        }

class CalendarTool(Tool):
    """Tool pour la gestion du calendrier"""
    
    def get_name(self) -> str:
        return "calendar"
    
    def get_description(self) -> str:
        return "Gère les rendez-vous et rappels"
    
    async def run(self, action: str, **kwargs) -> Dict:
        if action == "list":
            return {"events": ["Réunion équipe 14h", "Appel client 16h"]}
        elif action == "add":
            return {"status": "success", "message": "Événement ajouté"}
        return {"status": "error", "message": "Action non reconnue"}

class DomoticsTool(Tool):
    """Tool pour la domotique"""
    
    def get_name(self) -> str:
        return "domotics"
    
    def get_description(self) -> str:
        return "Contrôle les équipements domotiques"
    
    async def run(self, device: str, action: str, **kwargs) -> Dict:
        # Simulation de contrôle domotique
        return {
            "device": device,
            "action": action,
            "status": "success",
            "message": f"{device} {action} avec succès"
        }

class ToolManager:
    """Gestionnaire des tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.register_default_tools()
    
    def register_default_tools(self):
        """Enregistre les tools par défaut"""
        tools = [WeatherTool(), CalendarTool(), DomoticsTool()]
        for tool in tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: Tool):
        """Enregistre un nouveau tool"""
        self.tools[tool.get_name()] = tool
    
    def unregister_tool(self, name: str) -> bool:
        """Désenregistre un tool"""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Récupère un tool par nom"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """Liste tous les tools disponibles"""
        return list(self.tools.keys())
    
    async def run_tool(self, name: str, *args, **kwargs) -> Any:
        """Exécute un tool"""
        tool = self.get_tool(name)
        if tool:
            return await tool.run(*args, **kwargs)
        return {"error": f"Tool '{name}' non trouvé"}

# =============================================================================
# CONSCIENCE TEMPORELLE
# =============================================================================

class TimeManager:
    """Gestionnaire de la conscience temporelle"""
    
    def __init__(self):
        self.timezone = CONFIG["timezone"]
    
    def get_current_time(self) -> datetime:
        """Récupère l'heure actuelle"""
        return datetime.now()
    
    def get_time_period(self) -> str:
        """Détermine la période de la journée"""
        current_time = self.get_current_time().time()
        
        if time(6, 0) <= current_time < time(12, 0):
            return "matin"
        elif time(12, 0) <= current_time < time(18, 0):
            return "après-midi"
        elif time(18, 0) <= current_time < time(24, 0):
            return "soir"
        else:
            return "nuit"
    
    def get_temporal_context(self) -> Dict[str, Any]:
        """Récupère le contexte temporel complet"""
        now = self.get_current_time()
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "period": self.get_time_period(),
            "day_name": now.strftime("%A"),
            "month_name": now.strftime("%B")
        }

# =============================================================================
# INTERFACE AVEC OLLAMA
# =============================================================================

class OllamaClient:
    """Client pour interagir avec Ollama"""
    
    def __init__(self):
        self.base_url = CONFIG["ollama_url"]
        self.model = "llama3.2:1b"  # Modèle par défaut
    
    async def generate_response(self, messages: List[Dict], persona: Persona, 
                              context: Dict = None) -> str:
        """Génère une réponse avec Ollama"""
        # Construction du prompt avec persona et contexte
        system_prompt = self.build_system_prompt(persona, context)
        
        # Préparation des messages
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": formatted_messages,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "Désolé, je n'ai pas pu traiter votre demande.")
            else:
                return f"Erreur de communication avec Ollama: {response.status_code} ({self.base_url}/api/generate)"
                
        except Exception as e:
            return f"Erreur lors de la génération: {str(e)}"
    
    def build_system_prompt(self, persona: Persona, context: Dict = None) -> str:
        """Construit le prompt système avec persona et contexte"""
        prompt = f"""Tu es {persona.name}, {persona.description}.
        
Ton ton est {persona.tone}.
Tes réactions typiques sont: {', '.join(persona.reactions)}.
Tes préférences: {json.dumps(persona.preferences, ensure_ascii=False)}.
"""
        
        if context:
            if context.get("temporal"):
                temporal = context["temporal"]
                prompt += f"""
Contexte temporel:
- Date et heure: {temporal['datetime']}
- Période: {temporal['period']}
- Jour: {temporal['day_name']}
"""
            
            if context.get("memories"):
                prompt += f"""
Mémoires pertinentes:
{chr(10).join([f"- {memory['content']}" for memory in context["memories"]])}
"""
        
        prompt += """
Réponds de manière naturelle et cohérente avec ta personnalité.
Utilise le contexte temporel pour adapter tes réponses.
Si tu as besoin d'utiliser des outils, indique-le clairement.
"""
        
        return prompt

# =============================================================================
# ASSISTANT PRINCIPAL
# =============================================================================

class VirtualAssistant:
    """Assistant virtuel principal"""
    
    def __init__(self):
        self.persona_manager = PersonaManager()
        self.memory_manager = MemoryManager()
        self.tool_manager = ToolManager()
        self.time_manager = TimeManager()
        self.ollama_client = OllamaClient()
        self.current_persona = None
        self.session_active = False
    
    def load_persona(self, name: str) -> bool:
        """Charge une persona"""
        persona = self.persona_manager.get_persona(name)
        if persona:
            self.current_persona = persona
            return True
        return False
    
    async def process_query(self, query: str) -> str:
        """Traite une requête utilisateur"""
        if not self.current_persona:
            return "Aucune persona chargée. Utilisez 'va switch --persona [nom]' pour charger une persona."
        
        # Ajout à la mémoire de session
        self.memory_manager.add_to_session(query, "user")
        
        # Recherche dans la mémoire long terme
        relevant_memories = self.memory_manager.search_memories(query, top_k=3)
        
        # Contexte temporel
        temporal_context = self.time_manager.get_temporal_context()
        
        # Construction du contexte
        context = {
            "temporal": temporal_context,
            "memories": relevant_memories
        }
        
        # Historique de session
        session_context = self.memory_manager.get_session_context()
        messages = []
        for msg in session_context:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Génération de la réponse
        response = await self.ollama_client.generate_response(
            messages, self.current_persona, context
        )
        
        # Ajout de la réponse à la mémoire
        self.memory_manager.add_to_session(response, "assistant")
        
        # Sauvegarde périodique en mémoire long terme
        if len(self.memory_manager.session_memory) % 10 == 0:
            conversation_summary = f"Conversation avec {self.current_persona.name}: {query} -> {response}"
            self.memory_manager.add_to_long_term(conversation_summary, "conversation")
        
        return response

# =============================================================================
# INTERFACE CLI
# =============================================================================

# Instance globale de l'assistant
assistant = VirtualAssistant()

@app.command()
def start():
    """Démarre une session interactive"""
    console.print(Panel.fit(
        "[bold blue]Assistant Virtuel - Session Interactive[/bold blue]",
        style="blue"
    ))
    
    if not assistant.current_persona:
        console.print("[yellow]Chargement de la persona par défaut: Alice[/yellow]")
        assistant.load_persona("alice")
    
    console.print(f"[green]Persona active: {assistant.current_persona.name}[/green]")
    console.print("[dim]Tapez 'quit' pour quitter[/dim]\n")
    
    assistant.session_active = True
    
    while assistant.session_active:
        try:
            query = console.input("[bold cyan]Vous: [/bold cyan]")
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if query.strip():
                # Traitement asynchrone
                response = asyncio.run(assistant.process_query(query))
                
                console.print(f"[bold green]{assistant.current_persona.name}: [/bold green]{response}\n")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Erreur: {e}[/red]")
    
    console.print("\n[yellow]Session terminée[/yellow]")

@app.command()
def ask(question: str):
    """Pose une question à l'assistant"""
    if not assistant.current_persona:
        console.print("[yellow]Chargement de la persona par défaut: Alice[/yellow]")
        assistant.load_persona("alice")
    
    try:
        response = asyncio.run(assistant.process_query(question))
        console.print(f"[bold green]{assistant.current_persona.name}:[/bold green] {response}")
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")

@app.command()
def switch(persona: str):
    """Change la persona active"""
    if assistant.load_persona(persona):
        console.print(f"[green]Persona changée: {assistant.current_persona.name}[/green]")
    else:
        console.print(f"[red]Persona '{persona}' non trouvée[/red]")
        available = assistant.persona_manager.list_personas()
        console.print(f"[yellow]Personas disponibles: {', '.join(available)}[/yellow]")

@app.command()
def list_personas():
    """Liste toutes les personas disponibles"""
    personas = assistant.persona_manager.list_personas()
    console.print("[bold blue]Personas disponibles:[/bold blue]")
    for name in personas:
        persona = assistant.persona_manager.get_persona(name)
        marker = "→" if assistant.current_persona and assistant.current_persona.name.lower() == name else " "
        console.print(f"{marker} [cyan]{persona.name}[/cyan]: {persona.description}")

@app.command()
def list_tools():
    """Liste tous les tools disponibles"""
    tools = assistant.tool_manager.list_tools()
    console.print("[bold blue]Tools disponibles:[/bold blue]")
    for name in tools:
        tool = assistant.tool_manager.get_tool(name)
        console.print(f"• [cyan]{name}[/cyan]: {tool.get_description()}")

@app.command()
def time_info():
    """Affiche les informations temporelles"""
    context = assistant.time_manager.get_temporal_context()
    console.print(Panel.fit(
        f"[bold]Informations temporelles[/bold]\n"
        f"Date: {context['date']}\n"
        f"Heure: {context['time']}\n"
        f"Période: {context['period']}\n"
        f"Jour: {context['day_name']}\n"
        f"Mois: {context['month_name']}",
        style="blue"
    ))

@app.command()
def memory_stats():
    """Affiche les statistiques de mémoire"""
    session_count = len(assistant.memory_manager.session_memory)
    
    conn = sqlite3.connect(assistant.memory_manager.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memories")
    long_term_count = cursor.fetchone()[0]
    conn.close()
    
    console.print(Panel.fit(
        f"[bold]Statistiques de mémoire[/bold]\n"
        f"Mémoire de session: {session_count} éléments\n"
        f"Mémoire long terme: {long_term_count} éléments\n"
        f"Index vectoriel: {assistant.memory_manager.index.ntotal if assistant.memory_manager.index else 0} vecteurs",
        style="green"
    ))

if __name__ == "__main__":
    app()