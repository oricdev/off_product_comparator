# Utilise Python 3.14.4 comme base
FROM python:3.14.4-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le code source
COPY . .

# Installe les dépendances nécessaires
RUN pip install --no-cache-dir Flask==3.0.0 flask-cors pymongo six numpy

# Expose le port 5000
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "app.py"]
