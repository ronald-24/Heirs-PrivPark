### Objective

Describe the complete authentication flow (registration, login, logout) between a Flutter frontend using **Firebase Auth** and a FastAPI backend, based on official Firebase and Flutter documentation.

- Firebase reference (project `heirsprivpark`): `https://console.firebase.google.com/u/0/project/heirsprivpark/settings/general/web:ODJiYzhlNzYtYTRlOS00ZmY5LWIxOWItOWIxYWE3NjkxZjJh`
- Flutter/Firebase reference: same page to retrieve web configuration and follow integration guide.

---

## 1. Firebase Prerequisites

- **Create a Firebase project** ([Firebase console](https://console.firebase.google.com/)).
- **Enable Email/Password authentication** in Authentication > Sign-in method section.
- **Add a Flutter application** to the Firebase project:
  - Retrieve configuration (`google-services.json` for Android, `GoogleService-Info.plist` for iOS).
  - For web, retrieve JS config (`firebaseConfig`).
- **Download service key** (JSON) for backend (Project settings > Service accounts > Generate new private key).

### Recommended option: configuration via FlutterFire CLI

Automatically generate `firebase_options.dart` with correct identifiers for each platform:

```bash
npm i -g firebase-tools
dart pub global activate flutterfire_cli
flutterfire configure --project heirsprivpark
```

This creates `lib/firebase_options.dart` and allows Firebase initialization with `DefaultFirebaseOptions.currentPlatform` (see section 2.b).

---

## 2. Flutter Integration

### a. Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  firebase_core: ^2.0.0
  firebase_auth: ^4.0.0
  flutter_secure_storage: ^9.0.0
  http: ^1.0.0
```

### b. Firebase Initialization

With FlutterFire CLI (recommended):

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}
```

Without FlutterFire CLI (web only), use web config from Firebase console to initialize, but avoid versioning secrets.

### c. Registration (Sign Up)

```dart
final cred = await FirebaseAuth.instance.createUserWithEmailAndPassword(
  email: email,
  password: password,
);
final idToken = await cred.user?.getIdToken(true); // Retrieve Firebase ID Token
```

### d. Login (Sign In)

```dart
final cred = await FirebaseAuth.instance.signInWithEmailAndPassword(
  email: email,
  password: password,
);
final idToken = await cred.user?.getIdToken(true);
```

### e. Backend Call with Token

```dart
final headers = {
  'Authorization': 'Bearer $idToken',
  'Content-Type': 'application/json',
};
final response = await http.post(
  Uri.parse('http://localhost:8000/api/auth/login'),
  headers: headers,
);
```

### f. Logout (Sign Out)

```dart
await FirebaseAuth.instance.signOut();
// Purge any locally stored token (e.g., flutter_secure_storage)
```

---

## 3. Backend FastAPI

### a. Prérequis

- **Variables d’environnement** (voir `backend/app/core/config.py`) :
  - `FIREBASE_CREDENTIALS_PATH` : chemin du JSON de service Firebase.
  - `FIREBASE_PROJECT_ID` : ID du projet Firebase.
  - `DATABASE_URL` : URL de la base de données.
- **CORS** : ouverts via `CORSMiddleware` selon `cors_origins`.
- **Démarrage** : tables auto-créées au startup (`Base.metadata.create_all`).

### b. Sécurisation et CORS

- Limitez `CORS_ORIGINS` aux domaines de vos applications (par ex. `http://localhost:xxxx` en dev, vos domaines en prod).
- Le backend ne gère pas de sessions : la sécurité repose sur la **validation serveur de l’ID Token** Firebase à chaque requête protégée.

### c. Endpoints principaux

- `POST /api/auth/login` : vérifie le token, upsert l’utilisateur, retourne le profil (`UserOut`).
- `POST /api/auth/logout` : message informatif (aucun état serveur).
- `GET /api/auth/me` ou `GET /api/users/me` : retourne le profil courant.
- `PUT /api/users/me` : met à jour `display_name`/`photo_url`.

Tous les endpoints protégés requièrent l’en-tête : `Authorization: Bearer <Firebase ID Token>`.

---

## 4. Flow d’authentification complet

### a. Inscription (Sign Up)

1. **Flutter**
   - Créer un compte avec `createUserWithEmailAndPassword`.
   - Récupérer l’ID Token Firebase.
   - Appeler le backend : `POST /api/auth/login` avec l’en-tête Bearer.
2. **Backend**
   - Vérifie le token (`firebase_admin.auth.verify_id_token`).
   - Upsert l’utilisateur en base.
   - Retourne le profil (`UserOut`).
3. **(Optionnel) Mise à jour du profil**
   - `PUT /api/users/me` avec les champs à modifier.

### b. Connexion (Sign In)

1. **Flutter**
   - Se connecter avec `signInWithEmailAndPassword`.
   - Récupérer l’ID Token Firebase.
   - Appeler le backend : `POST /api/auth/login`.
2. **Backend**
   - Même logique que pour l’inscription.

### c. Déconnexion (Sign Out)

1. **Flutter**
   - Appeler `signOut()`.
   - Purger tout token stocké localement.
2. **Backend**
   - (Optionnel) `POST /api/auth/logout` (retourne un message, aucun état serveur).

---

## 5. Exemples d’appels cURL

**Connexion / Vérification**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Authorization: Bearer <ID_TOKEN>"
```

**Profil courant**

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <ID_TOKEN>"
```

**Mise à jour du profil**

```bash
curl -X PUT http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <ID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"display_name":"Jane","photo_url":"https://..."}'
```

---

## 6. Bonnes pratiques Flutter & Sécurité

- Toujours rafraîchir le token avant chaque appel :

```dart
final idToken = await FirebaseAuth.instance.currentUser?.getIdToken(true);
```

- Ne stockez pas le token à long terme ; utilisez `flutter_secure_storage` pour un cache court si besoin.
- Gérez les erreurs HTTP :
  - 401 Unauthorized : token manquant/invalide/expiré → rafraîchir le token, rediriger vers login.
  - 403 Forbidden : permissions insuffisantes.
- Ajoutez systématiquement l’en-tête `Authorization: Bearer <ID_TOKEN>` dans vos requêtes.

### Intercepteurs HTTP (Flutter)

Mettez en place un intercepteur (ex. wrapper `http` ou `dio`) qui :

- ajoute automatiquement l’ID Token courant dans `Authorization` ;
- en cas de 401, tente `getIdToken(true)` puis rejoue la requête une fois.

---

## 7. Backend : logique de vérification

**Extrait Python :**

```python
# app/api/deps.py
decoded = fb_auth.verify_id_token(id_token)
user = upsert_from_claims(
    db,
    firebase_uid=decoded.get("uid"),
    email=decoded.get("email"),
    display_name=decoded.get("name"),
    photo_url=decoded.get("picture"),
)
```

---

## 8. Points d’attention

- `FIREBASE_CREDENTIALS_PATH` doit pointer vers un JSON de compte de service valide.
- Les **ID Tokens expirent** rapidement ; le frontend doit gérer le refresh (Firebase le fait automatiquement).
- Tous les endpoints protégés exigent l’en-tête `Authorization: Bearer ...`.
- Le champ `password` existe dans le modèle mais n’est pas utilisé dans le flow Firebase (laisser `null`).
- Pour des providers tiers (Google/Apple), l’ID Token obtenu via Firebase Auth est validé de la même manière côté backend.
- En production, envisagez d’activer **App Check** et de restreindre les origines CORS.

---

## 9. Résumé du flow

- Inscription/connexion via **Firebase Auth** côté Flutter.
- Flutter récupère l’**ID Token** puis appelle les endpoints du backend avec l’en-tête Bearer.
- Le backend **vérifie le token**, upsert l’utilisateur et renvoie le profil.
- Déconnexion : **uniquement** côté Flutter.
- Profil courant : `GET /api/auth/me` ou `GET /api/users/me` ; mise à jour via `PUT /api/users/me`.

---

## 10. Rôles & Permissions

- `user`: accès normal à l'application
- `admin`: accès au back office (panel admin)

### Accès Admin

Les routes admin sont préfixées par `/admin` et nécessitent `role == "admin"`.

- `GET /admin/users` — liste des utilisateurs
- `PUT /admin/users/{user_id}` — mise à jour du rôle / statut actif
- `GET /admin/issue-reports` — liste des signalements de problèmes
- `PUT /admin/issue-reports/{issue_report_id}` — mise à jour du statut/note admin
