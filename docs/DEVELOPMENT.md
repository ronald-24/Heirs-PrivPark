# Guide de Développement - Heirs-PrivPark

## Structure du Projet

```
Heirs-PrivPark/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Routes API
│   │   ├── core/           # Configuration
│   │   ├── db/             # Base de données
│   │   └── schemas/        # Modèles Pydantic
│   ├── secrets/            # Clés Firebase
│   ├── .env               # Variables d'environnement
│   └── requirements.txt   # Dépendances Python
├── mobile/                # App Flutter (à créer)
├── docs/                  # Documentation
├── test/                  # Tests automatisés
└── README.md
```

## Configuration de l'environnement

### 1. Backend (FastAPI)

```bash
# Environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Dépendances
pip install -r backend/requirements.txt
```

### 2. Base de données PostgreSQL

```sql
-- Créer la base de données
CREATE DATABASE privpark;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE privpark TO postgres;
```

### 3. Configuration Firebase

1. Créer un projet Firebase
2. Activer Authentication (Email/Phone/Google)
3. Télécharger la clé de service Admin SDK
4. Placer dans `backend/secrets/firebase_service_account.json`

### 4. Variables d'environnement

Créer `backend/.env` :

```env
ENV=dev
PROJECT_NAME=HeirsPrivPark
API_PREFIX=/api
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/privpark
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=backend/secrets/firebase_service_account.json
CORS_ORIGINS=*
```

## Démarrage du serveur

```bash
# Démarrer le serveur de développement
python run_server.py

# Ou directement avec uvicorn
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Le serveur sera disponible sur http://127.0.0.1:8000

## Tests

### Tests d'authentification

```bash
# Tests de base
python backend/app/test/test_auth.py

# Tests avec token Firebase
python backend/app/test/test_auth.py YOUR_FIREBASE_TOKEN
```

### Tests manuels avec cURL

```bash
# Test de santé
curl http://127.0.0.1:8000/health

# Test avec token
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/users/me
```

## Développement

### Ajout de nouveaux endpoints

1. Créer la route dans `backend/app/api/routes_*.py`
2. Ajouter les schémas dans `backend/app/schemas/`
3. Ajouter les modèles DB si nécessaire
4. Tester avec le script de test

### Structure des routes

```python
from fastapi import APIRouter, Depends
from app.api.deps import verify_bearer_token_and_get_user

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/items")
def get_items(current_user = Depends(verify_bearer_token_and_get_user)):
    return {"items": []}
```

### Modèles de base de données

```python
# backend/app/db/models/example.py
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
```

### Schémas Pydantic

```python
# backend/app/schemas/example.py
from pydantic import BaseModel

class ExampleBase(BaseModel):
    name: str

class ExampleOut(ExampleBase):
    id: int
    class Config:
        from_attributes = True
```

## Debugging

### Logs

Les logs sont affichés dans la console du serveur.

### Base de données

```bash
# Connexion à PostgreSQL
psql -h localhost -U postgres -d privpark

# Voir les tables
\dt

# Voir les utilisateurs
SELECT * FROM users;
```

### Firebase

Vérifier les logs Firebase dans la console Firebase.

## Déploiement

### Production avec Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build et run
docker build -t heirsprivpark-api .
docker run -p 8000:8000 heirsprivpark-api
```

## Bonnes pratiques

### Code

- Utiliser des types Python stricts
- Documenter les fonctions avec docstrings
- Suivre PEP 8
- Tester avant de commiter

### Sécurité

- Ne jamais commiter les clés API
- Utiliser des variables d'environnement
- Valider toutes les entrées utilisateur
- Implémenter rate limiting en production

### Base de données

- Utiliser des migrations Alembic
- Créer des index sur les colonnes fréquemment utilisées
- Faire des sauvegardes régulières

## Troubleshooting

### Erreurs communes

1. **Erreur de connexion PostgreSQL**

   - Vérifier que PostgreSQL est démarré
   - Vérifier les credentials dans `.env`

2. **Erreur Firebase**

   - Vérifier que le fichier de clé existe
   - Vérifier le PROJECT_ID

3. **Erreur CORS**
   - Vérifier la configuration CORS_ORIGINS
   - Ajouter l'origine frontend

### Support

- Consulter les logs du serveur
- Vérifier la documentation API
- Créer une issue GitHub si nécessaire

