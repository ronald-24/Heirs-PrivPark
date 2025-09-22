# Documentation API - Heirs-PrivPark

## Base URL

```
http://127.0.0.1:8000  # Développement
https://api.heirsprivpark.com  # Production
```

## Authentification

Tous les endpoints protégés nécessitent un header d'autorisation :

```
Authorization: Bearer <FIREBASE_ID_TOKEN>
```

## Endpoints

### Santé du service

#### GET /health

Vérifier le statut de l'API.

**Response:**

```json
{
  "status": "ok"
}
```

---

### Authentification

#### POST /api/auth/verify-token

Vérifier un token Firebase et retourner les informations utilisateur.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "user_id": 1,
  "firebase_uid": "abc123...",
  "email": "user@example.com",
  "message": "Token valide"
}
```

#### POST /api/auth/login

Connexion utilisateur (alias pour verify-token).

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "John Doe",
  "photo_url": "https://...",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/auth/logout

Déconnexion (symbolique, la vraie déconnexion se fait côté client).

**Response:**

```json
{
  "message": "Logout réussi",
  "note": "Veuillez vous déconnecter depuis l'application mobile"
}
```

#### GET /api/auth/me

Récupérer les informations de l'utilisateur connecté.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "John Doe",
  "photo_url": "https://...",
  "role": "user"
}
```

---

### Utilisateurs

#### GET /api/users/me

Récupérer le profil détaillé de l'utilisateur connecté.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "John Doe",
  "photo_url": "https://...",
  "role": "user"
}
```

#### PUT /api/users/me

Modifier le profil de l'utilisateur connecté.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "display_name": "John Smith",
  "photo_url": "https://new-photo.com/avatar.jpg"
}
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "John Smith",
  "photo_url": "https://new-photo.com/avatar.jpg",
  "role": "user"
}
```

---

## Codes d'erreur

| Code | Description                                |
| ---- | ------------------------------------------ |
| 200  | Succès                                     |
| 401  | Non autorisé (token invalide/missing)      |
| 403  | Accès interdit (permissions insuffisantes) |
| 422  | Erreur de validation                       |
| 500  | Erreur serveur                             |

## Exemples d'utilisation

### JavaScript/Fetch

```javascript
const token = "YOUR_FIREBASE_ID_TOKEN";

// Récupérer le profil utilisateur
const response = await fetch("http://127.0.0.1:8000/api/users/me", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

const user = await response.json();
console.log(user);
```

### Python/Requests

```python
import requests

token = "YOUR_FIREBASE_ID_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# Vérifier le token
response = requests.post(
    "http://127.0.0.1:8000/api/auth/verify-token",
    headers=headers
)
print(response.json())
```

### cURL

```bash
# Test de santé
curl http://127.0.0.1:8000/health

# Récupérer le profil
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/users/me
```

## Swagger/OpenAPI

La documentation interactive est disponible à :

- **Développement**: http://127.0.0.1:8000/docs
- **Production**: https://api.heirsprivpark.com/docs

