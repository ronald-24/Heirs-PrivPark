# Heirs-PrivPark 🅿️

**Mobile application for private parking space rental**

A platform connecting parking space owners with users looking for safe and affordable parking.

## 🎯 Mission

Provide a practical, affordable and secure parking solution by connecting private space owners with users looking for parking.

## 🏗️ Architecture

### Frontend (Mobile)

- **Framework**: Flutter
- **Authentication**: Firebase Authentication
- **Maps**: Google Maps API
- **Payments**: Stripe Integration

### Backend (API)

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: Firebase Admin SDK
- **Storage**: AWS S3 (photos)
- **Notifications**: Firebase Cloud Messaging

## 🚀 MVP Features

### ✅ Phase 1 - Authentication (COMPLETED)

- [x] Registration/Login (Firebase Auth)
- [x] User profiles
- [x] Token verification
- [x] Role management (user/admin)

### 🔄 Phase 2 - Parking Management (IN PROGRESS)

- [ ] Add/Modify spaces
- [ ] Photos and descriptions
- [ ] Availability calendar
- [ ] Geolocation

### 📋 Phase 3 - Search and Booking

- [ ] Search by location
- [ ] Filters (price, date, availability)
- [ ] Real-time booking
- [ ] GPS navigation

### 💳 Phase 4 - Payments

- [ ] Stripe integration
- [ ] Secure payments
- [ ] Digital receipts
- [ ] Transaction history

### 🔔 Phase 5 - Notifications

- [ ] Booking confirmations
- [ ] Payment reminders
- [ ] Push notifications
- [ ] Dispute management

### 👨‍💼 Phase 6 - Administration

- [ ] Admin panel
- [ ] User management
- [ ] Listing moderation
- [ ] Customer support

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+
- Flutter 3.0+

### Backend (FastAPI)

```bash
# Clone the project
git clone <repository-url>
cd Heirs-PrivPark

# Virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Dependencies
pip install -r backend/requirements.txt

# Configuration
cp backend/env.example backend/.env
# Edit backend/.env with your Firebase keys

# Start the server
python run_server.py
```

### Frontend (Flutter)

```bash
cd mobile/
flutter pub get
flutter run
```

## 📡 API Endpoints

### Authentication

- `POST /api/auth/verify-token` - Verify Firebase token
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - User profile

### Users

- `GET /api/users/me` - Detailed profile
- `PUT /api/users/me` - Update profile

### Health

- `GET /health` - API status

## 🧪 Tests

```bash
# Authentication tests
python backend/app/test/test_auth.py

# Tests with Firebase token
python backend/app/test/test_auth.py YOUR_FIREBASE_TOKEN
```

## 🔧 Configuration

### Environment variables (backend/.env)

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

1. Create Firebase project
2. Enable Authentication (Email/Phone/Google)
3. Download Admin SDK service key
4. Place in `backend/secrets/`

## 📊 Database

### User Model

- `id` (Primary Key)
- `firebase_uid` (Unique)
- `email`, `display_name`, `photo_url`
- `role` (user/admin)
- `created_at`
