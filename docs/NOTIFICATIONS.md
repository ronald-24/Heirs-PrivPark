# Système de Notifications - Heirs PrivPark

## Vue d'ensemble

Le système de notifications de base a été implémenté pour fournir des notifications automatiques aux utilisateurs concernant leurs réservations et paiements, incluant des rappels périodiques toutes les 30 minutes pendant qu'une réservation est en cours.

## Fonctionnalités implémentées

### Types de notifications

1. **Confirmation de réservation** (`booking_confirmation`)

   - Envoyée quand une réservation est créée
   - Contient les détails de la réservation (parking, horaires, montant)

2. **Confirmation de paiement** (`payment_confirmation`)

   - Envoyée quand un paiement est réussi
   - Contient les détails du paiement et le lien vers le reçu

3. **Rappel de réservation** (`booking_reminder`)

   - Envoyée 1 heure avant le début de la réservation
   - Peut être programmée via un endpoint dédié

4. **Rappel de fin de réservation** (`booking_end_reminder`) ⭐ **NOUVEAU**

   - Envoyée toutes les 30 minutes pendant qu'une réservation est en cours
   - Rappelle à l'utilisateur la fin imminente de sa réservation
   - Contient le temps restant en minutes

5. **Annulation de réservation** (`booking_cancelled`)

   - Envoyée quand une réservation est annulée
   - Contient les détails de l'annulation

6. **Échec de paiement** (`payment_failed`)
   - Envoyée quand un paiement échoue
   - Contient les détails de l'erreur

## Structure de la base de données

### Table `notifications`

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type notificationtype NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data TEXT, -- JSON string pour données supplémentaires
    booking_id INTEGER REFERENCES bookings(id),
    payment_id INTEGER REFERENCES payments(id),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);
```

### Table `active_reminders` ⭐ **NOUVEAU**

```sql
CREATE TABLE active_reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    booking_id INTEGER NOT NULL REFERENCES bookings(id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    last_reminder_sent TIMESTAMP WITH TIME ZONE,
    reminder_interval_minutes INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Enum `notificationtype`

```sql
CREATE TYPE notificationtype AS ENUM (
    'booking_confirmation',
    'payment_confirmation',
    'booking_reminder',
    'booking_end_reminder',  -- ⭐ NOUVEAU
    'booking_cancelled',
    'payment_failed'
);
```

## API Endpoints

### Notifications utilisateur

- `GET /notifications/` - Récupérer les notifications de l'utilisateur
- `GET /notifications/stats` - Statistiques des notifications
- `GET /notifications/{id}` - Récupérer une notification spécifique
- `PATCH /notifications/{id}/read` - Marquer comme lue
- `POST /notifications/mark-all-read` - Marquer toutes comme lues
- `DELETE /notifications/{id}` - Supprimer une notification

### Administration et rappels ⭐ **NOUVEAU**

- `POST /admin/schedule-reminders` - Programmer les rappels de début de réservation
- `POST /admin/process-periodic-reminders` - Traiter les rappels périodiques (30min)
- `POST /admin/schedule-start-reminders` - Démarrer les rappels pour réservations en cours
- `GET /admin/my-active-reminders` - Récupérer les rappels actifs de l'utilisateur
- `POST /admin/stop-reminder/{booking_id}` - Arrêter les rappels pour une réservation

## Utilisation

### Intégration automatique

Les notifications sont automatiquement créées lors des événements suivants :

1. **Création de réservation** - Notification de confirmation
2. **Paiement réussi** - Notification de confirmation de paiement
3. **Annulation de réservation** - Notification d'annulation

### Programmation des rappels périodiques ⭐ **NOUVEAU**

Le système de rappels périodiques fonctionne en plusieurs étapes :

1. **Démarrage automatique** : Quand une réservation commence, les rappels périodiques sont automatiquement démarrés
2. **Traitement périodique** : Un endpoint doit être appelé toutes les 30 minutes pour traiter les rappels
3. **Nettoyage automatique** : Les rappels expirés sont automatiquement nettoyés

#### Configuration recommandée

```bash
# Cron job pour traiter les rappels toutes les 30 minutes
*/30 * * * * curl -X POST http://your-api/admin/process-periodic-reminders

# Cron job pour démarrer les rappels pour les réservations qui commencent (toutes les 5 minutes)
*/5 * * * * curl -X POST http://your-api/admin/schedule-start-reminders

# Cron job pour les rappels de début de réservation (toutes les heures)
0 * * * * curl -X POST http://your-api/admin/schedule-reminders
```

### Exemple d'utilisation

```python
from app.services.notification_service import NotificationService

# Créer une notification personnalisée
NotificationService.create_booking_confirmation_notification(
    db, booking, user
)

# Démarrer les rappels périodiques pour une réservation
NotificationService.start_booking_end_reminders(db, booking, user)

# Traiter tous les rappels en attente
notifications_sent = NotificationService.process_periodic_reminders(db)

# Arrêter les rappels pour une réservation
NotificationService.stop_booking_end_reminders(db, booking)
```

## Migration

Pour appliquer les changements à la base de données :

```bash
cd backend
alembic upgrade head
```

## Test

Un script de test amélioré est fourni pour vérifier le fonctionnement :

```bash
python test_notifications.py
```

Le script teste maintenant :

- ✅ Notifications de confirmation de réservation
- ✅ Démarrage des rappels périodiques
- ✅ Envoi de rappels toutes les 30 minutes
- ✅ Arrêt des rappels
- ✅ Nettoyage des rappels expirés
- ✅ Statistiques des notifications

## Structure des fichiers

```
backend/
├── app/
│   ├── db/
│   │   ├── models/
│   │   │   ├── notification.py          # Modèle Notification
│   │   │   └── active_reminder.py      # ⭐ NOUVEAU: Modèle ActiveReminder
│   │   └── repositories/
│   │       ├── notification_repo.py    # Repository pour les notifications
│   │       └── active_reminder_repo.py # ⭐ NOUVEAU: Repository pour les rappels actifs
│   ├── schemas/
│   │   └── notification.py              # Schémas Pydantic
│   ├── services/
│   │   └── notification_service.py     # Service de gestion des notifications
│   └── api/
│       ├── routes_notifications.py     # Routes API notifications
│       └── routes_reminders.py         # Routes pour les rappels (amélioré)
├── alembic/versions/
│   ├── 0004_add_notifications.py       # Migration notifications
│   └── 0005_add_active_reminders.py   # ⭐ NOUVEAU: Migration rappels actifs
└── test_notifications.py              # Script de test (amélioré)
```

## Fonctionnement des rappels périodiques ⭐ **NOUVEAU**

### Cycle de vie d'une réservation avec rappels

1. **Réservation créée** → Notification de confirmation
2. **Paiement réussi** → Notification de confirmation de paiement
3. **1 heure avant le début** → Rappel de début de réservation
4. **Début de réservation** → Démarrage automatique des rappels périodiques
5. **Pendant la réservation** → Rappel toutes les 30 minutes
6. **Fin de réservation** → Arrêt automatique des rappels

### Gestion intelligente des rappels

- **Évite les doublons** : Vérifie qu'un rappel n'a pas déjà été envoyé dans l'intervalle
- **Nettoyage automatique** : Supprime les rappels pour les réservations terminées
- **Gestion d'erreurs** : Continue le traitement même si une notification échoue
- **Statistiques** : Retourne le nombre de notifications envoyées

## Exemples de notifications

### Confirmation de réservation

```json
{
  "type": "booking_confirmation",
  "title": "Réservation confirmée",
  "message": "Votre réservation pour le parking #123 a été créée avec succès. Début: 15/01/2024 à 14:00",
  "data": {
    "booking_id": 456,
    "parking_space_id": 123,
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T16:00:00Z",
    "total_amount": 20.0,
    "currency": "usd"
  }
}
```

### Rappel de fin de réservation

```json
{
  "type": "booking_end_reminder",
  "title": "Rappel de fin de réservation",
  "message": "Votre réservation pour le parking #123 se termine dans 30 minutes. Fin prévue: 15/01/2024 à 16:00",
  "data": {
    "booking_id": 456,
    "parking_space_id": 123,
    "end_time": "2024-01-15T16:00:00Z",
    "minutes_remaining": 30,
    "reminder_type": "end_reminder"
  }
}
```

### Confirmation de paiement

```json
{
  "type": "payment_confirmation",
  "title": "Paiement confirmé",
  "message": "Votre paiement de 20.0 USD a été traité avec succès. Votre réservation est maintenant confirmée.",
  "data": {
    "payment_id": 789,
    "booking_id": 456,
    "amount": 20.0,
    "currency": "usd",
    "payment_date": "2024-01-15T13:30:00Z",
    "receipt_url": "https://pay.stripe.com/receipts/..."
  }
}
```

## Gestion des erreurs

Le système de notifications est conçu pour être robuste :

- **Notifications non bloquantes** : Les erreurs de notification n'affectent pas les opérations principales
- **Logging des erreurs** : Toutes les erreurs sont loggées pour le debugging
- **Retry automatique** : Possibilité d'implémenter un système de retry
- **Fallback** : En cas d'échec, les données sont conservées pour retry ultérieur

## Monitoring et statistiques

### Endpoints de monitoring

- `GET /notifications/stats` - Statistiques par utilisateur
- `GET /admin/my-active-reminders` - Rappels actifs par utilisateur

### Métriques disponibles

- Nombre total de notifications
- Nombre de notifications non lues
- Répartition par type de notification
- Nombre de rappels actifs
- Nombre de notifications envoyées par traitement

## Sécurité

- **Authentification requise** : Tous les endpoints utilisateur nécessitent une authentification
- **Isolation des données** : Les utilisateurs ne peuvent accéder qu'à leurs propres notifications
- **Validation des données** : Toutes les données d'entrée sont validées
- **Protection CSRF** : Les endpoints utilisent les tokens d'authentification appropriés

## Performance

### Optimisations implémentées

- **Index sur les colonnes fréquemment utilisées** : `user_id`, `booking_id`, `created_at`
- **Pagination** : Limite par défaut de 50 notifications avec possibilité d'augmenter
- **Nettoyage automatique** : Suppression des rappels expirés
- **Requêtes optimisées** : Utilisation de jointures efficaces

### Recommandations

- **Archivage** : Considérer l'archivage des anciennes notifications
- **Cache** : Implémenter un cache Redis pour les statistiques fréquentes
- **Batch processing** : Traiter les notifications par lots pour de gros volumes

## Prochaines étapes

Pour étendre le système de notifications :

1. **Notifications push** - Intégration avec Firebase Cloud Messaging
2. **Notifications email** - Envoi d'emails automatiques
3. **Notifications SMS** - Intégration avec un service SMS
4. **Préférences utilisateur** - Permettre aux utilisateurs de configurer leurs préférences
5. **Templates** - Système de templates pour les messages
6. **Historique** - Archivage des anciennes notifications
7. **Analytics** - Statistiques d'engagement des notifications
8. **Rappels personnalisés** - Permettre aux utilisateurs de définir leurs propres intervalles
9. **Notifications géolocalisées** - Rappels basés sur la proximité du parking
10. **Notifications multi-langues** - Support de plusieurs langues

## Support et maintenance

### Logs à surveiller

- Erreurs de création de notifications
- Échecs d'envoi de rappels périodiques
- Problèmes de nettoyage des rappels expirés
- Erreurs d'authentification sur les endpoints

### Maintenance régulière

- Vérifier les cron jobs
- Surveiller les performances des requêtes
- Nettoyer les anciennes notifications si nécessaire
- Mettre à jour les templates de messages

## Conclusion

Le système de notifications de Heirs PrivPark fournit une solution complète pour informer les utilisateurs de l'état de leurs réservations et paiements. Avec les rappels périodiques toutes les 30 minutes, les utilisateurs sont toujours informés du temps restant de leur réservation, améliorant ainsi leur expérience utilisateur et réduisant les risques de dépassement de temps.
