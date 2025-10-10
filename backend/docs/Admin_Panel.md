# Admin Panel (Back Office) 🛠️

**Documentation complète du panneau d'administration pour Heirs-PrivPark**

## 📋 Vue d'ensemble

Le panneau d'administration permet aux administrateurs de gérer efficacement la plateforme de location de parkings privés. Il comprend la gestion des utilisateurs, la modération des annonces et la résolution des signalements de problèmes.

## 🔐 Authentification et autorisation

### Prérequis

- **Rôle requis** : `admin` (défini dans le champ `role` de la table `users`)
- **Authentification** : Token Firebase valide via header `Authorization: Bearer <token>`
- **Vérification** : Toutes les routes admin utilisent `require_role("admin", user.role)`

### Créer un utilisateur admin

```sql
-- Via SQL direct
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';

-- Ou via l'API (si vous avez déjà un admin)
PUT /admin/users/{user_id}
{
  "role": "admin"
}
```

## 👥 Gestion des utilisateurs

### 1. Lister tous les utilisateurs

**Endpoint** : `GET /admin/users`

**Réponse** :

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Utilisation** :

- Voir tous les utilisateurs inscrits
- Identifier les comptes inactifs
- Surveiller l'activité des utilisateurs

### 2. Modifier un utilisateur

**Endpoint** : `PUT /admin/users/{user_id}`

**Body** :

```json
{
  "role": "admin", // Optionnel : "user" ou "admin"
  "is_active": false // Optionnel : true/false
}
```

**Cas d'usage** :

- **Promouvoir un utilisateur** : `role: "admin"`
- **Suspendre un compte** : `is_active: false`
- **Réactiver un compte** : `is_active: true`

**Exemple** :

```bash
curl -X PUT "http://localhost:8000/admin/users/123" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "is_active": true}'
```

## 🅿️ Modération des annonces

### 1. Approuver/Rejeter une annonce

**Endpoint** : `PUT /admin/listings/{parking_id}/status`

**Paramètres** :

- `status` (requis) : `"pending"`, `"approved"`, `"rejected"`
- `is_active` (optionnel) : `true`/`false`

**Exemples** :

**Approuver une annonce** :

```bash
curl -X PUT "http://localhost:8000/admin/listings/456/status?status=approved" \
  -H "Authorization: Bearer <admin_token>"
```

**Rejeter une annonce** :

```bash
curl -X PUT "http://localhost:8000/admin/listings/456/status?status=rejected" \
  -H "Authorization: Bearer <admin_token>"
```

**Désactiver temporairement** :

```bash
curl -X PUT "http://localhost:8000/admin/listings/456/status?status=approved&is_active=false" \
  -H "Authorization: Bearer <admin_token>"
```

### 2. États des annonces

| État       | Description              | Visibilité |
| ---------- | ------------------------ | ---------- |
| `pending`  | En attente de modération | ❌ Masquée |
| `approved` | Approuvée par l'admin    | ✅ Visible |
| `rejected` | Rejetée par l'admin      | ❌ Masquée |

**Logique de filtrage** :

- Seules les annonces avec `status = "approved"` ET `is_active = true` apparaissent dans les recherches
- Les propriétaires peuvent toujours voir leurs annonces, même rejetées

## 🚨 Gestion des signalements (Issue Reports)

### 1. Lister tous les signalements

**Endpoint** : `GET /admin/issue-reports`

**Réponse** :

```json
[
  {
    "id": 1,
    "created_by_user_id": 123,
    "booking_id": 456,
    "parking_space_id": 789,
    "subject": "Place de parking en mauvais état",
    "description": "La place est très étroite et le sol est cassé...",
    "status": "open",
    "admin_notes": null,
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  }
]
```

### 2. Traiter un signalement

**Endpoint** : `PUT /admin/issue-reports/{issue_report_id}`

**Body** :

```json
{
  "status": "resolved", // "open", "in_review", "resolved", "dismissed"
  "admin_notes": "Remboursement de 50% accordé. Propriétaire contacté pour améliorer la signalisation."
}
```

**États des signalements** :

| État        | Description         | Action requise        |
| ----------- | ------------------- | --------------------- |
| `open`      | Nouveau signalement | Examiner le problème  |
| `in_review` | En cours d'examen   | Contacter les parties |
| `resolved`  | Résolu              | Fermer le dossier     |
| `dismissed` | Rejeté              | Motiver la décision   |

### 3. Exemples de résolution

**Signalement résolu avec remboursement** :

```json
{
  "status": "resolved",
  "admin_notes": "Problème confirmé. Remboursement de 50% accordé (7.50€). Propriétaire averti pour améliorer la qualité."
}
```

**Signalement rejeté** :

```json
{
  "status": "dismissed",
  "admin_notes": "Photos vérifiées - l'annonce correspond à la réalité. Aucune action requise."
}
```

## 📊 Tableau de bord admin

### Métriques clés à surveiller

```python
# Exemple de requêtes pour le dashboard
dashboard_stats = {
    "users": {
        "total": "SELECT COUNT(*) FROM users",
        "active": "SELECT COUNT(*) FROM users WHERE is_active = true",
        "admins": "SELECT COUNT(*) FROM users WHERE role = 'admin'"
    },
    "listings": {
        "total": "SELECT COUNT(*) FROM parking_spaces",
        "pending": "SELECT COUNT(*) FROM parking_spaces WHERE status = 'pending'",
        "approved": "SELECT COUNT(*) FROM parking_spaces WHERE status = 'approved'",
        "rejected": "SELECT COUNT(*) FROM parking_spaces WHERE status = 'rejected'"
    },
    "issue_reports": {
        "total": "SELECT COUNT(*) FROM issue_reports",
        "open": "SELECT COUNT(*) FROM issue_reports WHERE status = 'open'",
        "in_review": "SELECT COUNT(*) FROM issue_reports WHERE status = 'in_review'",
        "resolved": "SELECT COUNT(*) FROM issue_reports WHERE status = 'resolved'"
    },
    "bookings": {
        "total": "SELECT COUNT(*) FROM bookings",
        "confirmed": "SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'",
        "pending": "SELECT COUNT(*) FROM bookings WHERE status = 'pending'"
    }
}
```

## 🔄 Workflow de modération

### 1. Nouvelle annonce créée

```
Propriétaire crée annonce → status: "pending" → Admin reçoit notification → Admin examine → Approuve/Rejette
```

### 2. Signalement créé

```
Utilisateur signale problème → status: "open" → Admin examine → Met en "in_review" → Résout ou Rejette
```

### 3. Actions préventives

- **Surveillance** : Vérifier régulièrement les annonces en attente
- **Réactivité** : Traiter les signalements dans les 24h
- **Communication** : Informer les propriétaires des décisions

## 🛡️ Bonnes pratiques de sécurité

### 1. Vérification des permissions

```python
# Toujours vérifier le rôle admin
user, _ = verify_bearer_token_and_get_user(authorization=Authorization, db=db)
require_role("admin", user.role)
```

### 2. Validation des données

- Vérifier l'existence des ressources avant modification
- Valider les statuts autorisés
- Logger toutes les actions admin

### 3. Audit trail

```python
# Exemple de log d'action admin
admin_action_log = {
    "admin_id": user.id,
    "action": "approve_listing",
    "target_id": parking_id,
    "timestamp": datetime.now(),
    "details": {"status": "approved"}
}
```

## 📱 Interface utilisateur recommandée

### Sections principales

1. **Dashboard** : Vue d'ensemble des métriques
2. **Utilisateurs** : Liste et gestion des comptes
3. **Annonces** : Modération des parkings
4. **Signalements** : Résolution des problèmes
5. **Statistiques** : Rapports et analyses

### Fonctionnalités UX

- **Filtres** : Par statut, date, utilisateur
- **Recherche** : Par ID, email, sujet
- **Actions en lot** : Sélection multiple
- **Notifications** : Alertes pour nouvelles actions

## 🚀 Déploiement et configuration

### Variables d'environnement

```bash
# Admin par défaut (optionnel)
DEFAULT_ADMIN_EMAIL=admin@heirsprivpark.com

# Notifications admin
ADMIN_NOTIFICATION_EMAIL=admin@heirsprivpark.com
```

### Migration de base de données

```bash
# Appliquer les migrations
cd backend
alembic upgrade head

# Vérifier les nouvelles tables
psql -d privpark -c "\dt"
```

## 🔧 Maintenance et monitoring

### Tâches régulières

- **Quotidien** : Examiner les nouveaux signalements
- **Hebdomadaire** : Analyser les métriques d'utilisation
- **Mensuel** : Nettoyer les données anciennes

### Alertes recommandées

- Nouveau signalement urgent
- Annonce en attente > 24h
- Utilisateur suspendu
- Problème technique détecté

