# Redémarrage avec le projet Python

## python --version

Python 3.14.4

## Démarrage en ligne de commande
```
source .venv/bin/activate
python -c "import six; print(six.__version__)"
python app.py
```

http://192.168.1.149:5000/

## A suivre:

- docker mongo_prosim
- tester avec
```javascript
mongosh "mongodb://localhost:27018"
```
- `Querier.py`: changer l'url de connexion
- relancer l'app:
```javascript
python app.py
```
- tester un `Go!`