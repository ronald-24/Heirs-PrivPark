# Heirs-PrivPark 🅿️

**Application mobile de location de places de parking privées**

Une plateforme connectant les propriétaires de places de parking avec les utilisateurs cherchant un stationnement sûr et abordable.

## 🎯 Mission

Fournir une solution de stationnement pratique, abordable et sécurisée en connectant les propriétaires de places privées avec les utilisateurs en recherche de parking.

## 🏗️ Architecture

### Frontend (Mobile)

- **Framework**: Flutter
- **Authentification**: Firebase Authentication
- **Maps**: Google Maps API
- **Paiements**: Stripe Integration

### Backend (API)

- **Framework**: FastAPI (Python)
- **Base de données**: PostgreSQL
- **Authentification**: Firebase Admin SDK
- **Stockage**: AWS S3 (photos)
- **Notifications**: Firebase Cloud Messaging

## 🚀 Fonctionnalités MVP

### ✅ Phase 1 - Authentification (TERMINÉE)

- [x] Inscription/Connexion (Firebase Auth)
- [x] Profils utilisateurs
- [x] Vérification des tokens
- [x] Gestion des rôles (utilisateur/admin)

### 🔄 Phase 2 - Gestion des parkings (EN COURS)

- [ ] Ajout/Modification de places
- [ ] Photos et descriptions
- [ ] Calendrier de disponibilité
- [ ] Géolocalisation

### 📋 Phase 3 - Recherche et réservation

- [ ] Recherche par localisation
- [ ] Filtres (prix, date, disponibilité)
- [ ] Réservation en temps réel
- [ ] Navigation GPS

### 💳 Phase 4 - Paiements

- [ ] Intégration Stripe
- [ ] Paiements sécurisés
- [ ] Reçus numériques
- [ ] Historique des transactions

### 🔔 Phase 5 - Notifications

- [ ] Confirmations de réservation
- [ ] Rappels de paiement
- [ ] Notifications push
- [ ] Gestion des disputes

### 👨‍💼 Phase 6 - Administration

- [ ] Panel admin
- [ ] Gestion des utilisateurs
- [ ] Modération des annonces
- [ ] Support client

## 🛠️ Installation & Démarrage

### Prérequis

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+
- Flutter 3.0+

### Backend (FastAPI)

```bash
# Cloner le projet
git clone <repository-url>
cd Heirs-PrivPark

# Environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Dépendances
pip install -r backend/requirements.txt

# Configuration
cp backend/env.example backend/.env
# Éditer backend/.env avec vos clés Firebase

# Démarrer le serveur
python run_server.py
```

### Frontend (Flutter)

```bash
cd mobile/
flutter pub get
flutter run
```

## 📡 API Endpoints

### Authentification

- `POST /api/auth/verify-token` - Vérifier token Firebase
- `POST /api/auth/login` - Connexion utilisateur
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Profil utilisateur

### Utilisateurs

- `GET /api/users/me` - Profil détaillé
- `PUT /api/users/me` - Modifier profil

### Santé

- `GET /health` - Statut de l'API

## 🧪 Tests

```bash
# Tests d'authentification
python backend/app/test/test_auth.py

# Tests avec token Firebase
python backend/app/test/test_auth.py YOUR_FIREBASE_TOKEN
```

## 🔧 Configuration

### Variables d'environnement (backend/.env)

```env
ENV=dev
PROJECT_NAME=HeirsPrivPark
API_PREFIX=/api
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/privpark
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=backend/secrets/firebase_service_account.json
CORS_ORIGINS=*
```

### Firebase Setup

1. Créer projet Firebase
2. Activer Authentication (Email/Phone/Google)
3. Télécharger clé de service Admin SDK
4. Placer dans `backend/secrets/`

## 📊 Base de données

### Modèle User

- `id` (Primary Key)
- `firebase_uid` (Unique)
- `email`, `display_name`, `photo_url`
- `role` (user/admin)
- `created_at`
