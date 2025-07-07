# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Installation du package
RUN pip install -e .

# Création du répertoire de données
RUN mkdir -p /app/data

# Point d'entrée
ENTRYPOINT ["va"]
CMD ["--help"]