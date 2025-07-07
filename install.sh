#!/bin/bash

# Installation de l'Assistant Virtuel - Phase 1

echo "🚀 Installation de l'Assistant Virtuel - Phase 1"
echo "================================================="

# Vérification de Python 3.13
echo "📋 Vérification de Python 3.13..."
python_version=$(python3 --version 2>/dev/null | grep -o "3\.[0-9]\+")
if [[ "$python_version" < "3.13" ]]; then
    echo "❌ Python 3.13 ou supérieur requis"
    exit 1
fi

# Création de l'environnement virtuel
echo "🐍 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Installation du package
echo "🔧 Installation du package..."
pip install -e .

# Vérification d'Ollama
echo "🤖 Vérification d'Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama n'est pas installé"
    echo "   Installez-le depuis: https://ollama.com/download"
    echo "   Puis exécutez: ollama pull llama3.1:latest"
else
    echo "✅ Ollama détecté"
    
    # Vérification du modèle
    if ! ollama list | grep -q "llama3.1:latest"; then
        echo "📥 Téléchargement du modèle llama3.1:latest..."
        ollama pull llama3.1:latest
    fi
fi

# Création de la structure de données
echo "🗂️  Création de la structure de données..."
mkdir -p ~/.va_assistant

# Tests
echo "🧪 Exécution des tests..."
python -m pytest tests/ -v

echo "✅ Installation terminée!"
echo ""
echo "🎯 Pour commencer:"
echo "   source venv/bin/activate"
echo "   va start"
echo ""
echo "📖 Commandes disponibles:"
echo "   va start              - Démarre une session interactive"
echo "   va ask \"question\"     - Pose une question"
echo "   va switch --persona X - Change de persona"
echo "   va list-personas      - Liste les personas"
echo "   va list-tools         - Liste les tools"
echo "   va time-info          - Infos temporelles"
echo "   va memory-stats       - Statistiques mémoire"