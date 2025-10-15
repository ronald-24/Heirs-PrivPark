# API Documentation - Heirs-PrivPark

## Base URL

```
http://127.0.0.1:8000  # Development
https://api.heirsprivpark.com  # Production
```

## Authentication

All protected endpoints require an authorization header:

```
Authorization: Bearer <FIREBASE_ID_TOKEN>
```

## Endpoints

### Health Check

#### GET /health

Check API status.

**Response:**

```json
{
  "status": "ok"
}
```

---

### Authentication

#### POST /api/auth/verify-token

Verify a Firebase token and return user information.

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

#### GET /api/auth/me

Get current user information.

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

### Users

#### GET /api/users/me

Get detailed profile of the authenticated user.

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

Update the profile of the authenticated user.

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

### Parking Spaces

#### POST /api/parking/

Create a new parking space.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "title": "Downtown Parking Spot",
  "description": "Secure parking in downtown area",
  "photos": ["https://example.com/photo1.jpg"],
  "price_per_hour": 5.5,
  "rules": "No overnight parking",
  "address": "123 Main St, City",
  "latitude": 40.7128,
  "longitude": -74.006,
  "is_active": true,
  "status": "available"
}
```

**Response:**

```json
{
  "id": 1,
  "title": "Downtown Parking Spot",
  "description": "Secure parking in downtown area",
  "photos": ["https://example.com/photo1.jpg"],
  "price_per_hour": 5.5,
  "rules": "No overnight parking",
  "address": "123 Main St, City",
  "latitude": 40.7128,
  "longitude": -74.006,
  "is_active": true,
  "status": "available",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/parking/

List all parking spaces owned by the authenticated user.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
[
  {
    "id": 1,
    "title": "Downtown Parking Spot",
    "description": "Secure parking in downtown area",
    "photos": ["https://example.com/photo1.jpg"],
    "price_per_hour": 5.5,
    "rules": "No overnight parking",
    "address": "123 Main St, City",
    "latitude": 40.7128,
    "longitude": -74.006,
    "is_active": true,
    "status": "available",
    "owner_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/parking/{parking_id}

Get a specific parking space by ID.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "title": "Downtown Parking Spot",
  "description": "Secure parking in downtown area",
  "photos": ["https://example.com/photo1.jpg"],
  "price_per_hour": 5.5,
  "rules": "No overnight parking",
  "address": "123 Main St, City",
  "latitude": 40.7128,
  "longitude": -74.006,
  "is_active": true,
  "status": "available",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/parking/{parking_id}

Update a parking space.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "title": "Updated Parking Spot",
  "price_per_hour": 6.0
}
```

**Response:**

```json
{
  "id": 1,
  "title": "Updated Parking Spot",
  "description": "Secure parking in downtown area",
  "photos": ["https://example.com/photo1.jpg"],
  "price_per_hour": 6.0,
  "rules": "No overnight parking",
  "address": "123 Main St, City",
  "latitude": 40.7128,
  "longitude": -74.006,
  "is_active": true,
  "status": "available",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /api/parking/{parking_id}

Delete a parking space.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "ok": true
}
```

#### POST /api/parking/{parking_id}/availability

Add availability for a parking space.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "start": "2024-01-01T09:00:00Z",
  "end": "2024-01-01T17:00:00Z"
}
```

**Response:**

```json
{
  "id": 1,
  "start": "2024-01-01T09:00:00Z",
  "end": "2024-01-01T17:00:00Z"
}
```

#### GET /api/parking/{parking_id}/availability

Get availability for a parking space.

**Response:**

```json
[
  {
    "id": 1,
    "start": "2024-01-01T09:00:00Z",
    "end": "2024-01-01T17:00:00Z"
  }
]
```

#### DELETE /api/parking/availability/{availability_id}

Delete availability for a parking space.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "ok": true
}
```

#### POST /api/parking/{parking_id}/photos

Upload a photo for a parking space.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`
- `Content-Type: multipart/form-data`

**Body:**

- `file`: Image file

**Response:**

```json
{
  "url": "https://s3.amazonaws.com/bucket/photo.jpg"
}
```

#### GET /api/parking/search

Search for parking spaces.

**Query Parameters:**

- `lat` (float, required): Latitude
- `lng` (float, required): Longitude
- `radius_m` (float, optional): Search radius in meters (default: 3000, min: 100, max: 20000)
- `start_time` (string, optional): Start time in ISO format
- `end_time` (string, optional): End time in ISO format
- `max_price` (float, optional): Maximum price per hour
- `sort` (string, optional): Sort by "distance" or "price" (default: "distance")
- `limit` (int, optional): Number of results (default: 50, min: 1, max: 100)
- `offset` (int, optional): Offset for pagination (default: 0)

**Response:**

```json
[
  {
    "id": 1,
    "title": "Downtown Parking Spot",
    "address": "123 Main St, City",
    "latitude": 40.7128,
    "longitude": -74.006,
    "price_per_hour": 5.5,
    "distance_m": 250.5
  }
]
```

---

### Bookings

#### POST /api/bookings/

Create a new booking.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "parking_space_id": 1,
  "start_time": "2024-01-01T09:00:00Z",
  "end_time": "2024-01-01T17:00:00Z"
}
```

**Response:**

```json
{
  "id": 1,
  "user_id": 1,
  "parking_space_id": 1,
  "start_time": "2024-01-01T09:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "total_amount": 44.0,
  "currency": "usd",
  "status": "pending",
  "stripe_checkout_session_id": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/bookings/

Get all bookings for the authenticated user.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "parking_space_id": 1,
    "start_time": "2024-01-01T09:00:00Z",
    "end_time": "2024-01-01T17:00:00Z",
    "total_amount": 44.0,
    "currency": "usd",
    "status": "pending",
    "stripe_checkout_session_id": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/bookings/{booking_id}

Get a specific booking by ID.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "user_id": 1,
  "parking_space_id": 1,
  "start_time": "2024-01-01T09:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "total_amount": 44.0,
  "currency": "usd",
  "status": "pending",
  "stripe_checkout_session_id": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /api/bookings/{booking_id}

Cancel a booking.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "user_id": 1,
  "parking_space_id": 1,
  "start_time": "2024-01-01T09:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "total_amount": 44.0,
  "currency": "usd",
  "status": "cancelled",
  "stripe_checkout_session_id": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/bookings/profile

Get driver profile with booking statistics.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "user_id": 1,
  "display_name": "John Doe",
  "email": "john@example.com",
  "photo_url": "https://example.com/photo.jpg",
  "total_bookings": 10,
  "upcoming_bookings": 2,
  "past_bookings": 8,
  "total_spent": 250.0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/bookings/history

Get booking history with upcoming and past bookings.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Query Parameters:**

- `limit` (int, optional): Number of results (default: 50)
- `offset` (int, optional): Offset for pagination (default: 0)

**Response:**

```json
{
  "upcoming_bookings": [
    {
      "id": 1,
      "user_id": 1,
      "parking_space_id": 1,
      "start_time": "2024-01-01T09:00:00Z",
      "end_time": "2024-01-01T17:00:00Z",
      "total_amount": 44.0,
      "currency": "usd",
      "status": "confirmed",
      "stripe_checkout_session_id": "cs_123",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "parking_space_title": "Downtown Parking Spot",
      "parking_space_address": "123 Main St, City",
      "parking_space_latitude": 40.7128,
      "parking_space_longitude": -74.006
    }
  ],
  "past_bookings": [],
  "total_upcoming": 1,
  "total_past": 0
}
```

#### POST /api/bookings/rebook/{parking_space_id}

Rebook the same parking space with new time slot.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "start_time": "2024-01-02T09:00:00Z",
  "end_time": "2024-01-02T17:00:00Z"
}
```

**Response:**

```json
{
  "id": 2,
  "user_id": 1,
  "parking_space_id": 1,
  "start_time": "2024-01-02T09:00:00Z",
  "end_time": "2024-01-02T17:00:00Z",
  "total_amount": 44.0,
  "currency": "usd",
  "status": "pending",
  "stripe_checkout_session_id": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Payments

#### POST /api/payments/create-checkout-session

Create a Stripe checkout session for payment.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "booking_id": 1,
  "success_url": "https://app.example.com/success",
  "cancel_url": "https://app.example.com/cancel"
}
```

**Response:**

```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_123"
}
```

#### POST /api/payments/webhook

Stripe webhook endpoint for payment processing.

**Headers:**

- `Stripe-Signature`: Stripe signature header

**Body:**

- Raw webhook payload from Stripe

**Response:**

```json
{
  "received": true
}
```

---

### Issue Reports

#### POST /api/issue-reports/

Create a new issue report.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "subject": "Parking space not available",
  "description": "The parking space was occupied when I arrived",
  "booking_id": 1,
  "parking_space_id": 1
}
```

**Response:**

```json
{
  "id": 1,
  "created_by_user_id": 1,
  "booking_id": 1,
  "parking_space_id": 1,
  "subject": "Parking space not available",
  "description": "The parking space was occupied when I arrived",
  "status": "open",
  "admin_notes": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/issue-reports/{issue_report_id}

Update an issue report.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "subject": "Updated issue description",
  "description": "More detailed description of the issue"
}
```

**Response:**

```json
{
  "id": 1,
  "created_by_user_id": 1,
  "booking_id": 1,
  "parking_space_id": 1,
  "subject": "Updated issue description",
  "description": "More detailed description of the issue",
  "status": "open",
  "admin_notes": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Notifications

#### GET /api/notifications/

Get notifications for the authenticated user.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Query Parameters:**

- `limit` (int, optional): Number of results (default: 50, max: 100)
- `offset` (int, optional): Offset for pagination (default: 0)
- `unread_only` (bool, optional): Show only unread notifications (default: false)

**Response:**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "type": "booking_confirmation",
    "title": "Booking Confirmed",
    "message": "Your parking booking has been confirmed",
    "data": {
      "booking_id": 1,
      "parking_space_title": "Downtown Parking Spot"
    },
    "booking_id": 1,
    "payment_id": null,
    "is_read": false,
    "created_at": "2024-01-01T00:00:00Z",
    "read_at": null
  }
]
```

#### GET /api/notifications/stats

Get notification statistics for the authenticated user.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "total": 10,
  "unread": 3,
  "by_type": {
    "booking_confirmation": 5,
    "payment_confirmation": 3,
    "booking_reminder": 2
  }
}
```

#### GET /api/notifications/{notification_id}

Get a specific notification by ID.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "user_id": 1,
  "type": "booking_confirmation",
  "title": "Booking Confirmed",
  "message": "Your parking booking has been confirmed",
  "data": {
    "booking_id": 1,
    "parking_space_title": "Downtown Parking Spot"
  },
  "booking_id": 1,
  "payment_id": null,
  "is_read": false,
  "created_at": "2024-01-01T00:00:00Z",
  "read_at": null
}
```

#### PATCH /api/notifications/{notification_id}/read

Mark a notification as read.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "id": 1,
  "user_id": 1,
  "type": "booking_confirmation",
  "title": "Booking Confirmed",
  "message": "Your parking booking has been confirmed",
  "data": {
    "booking_id": 1,
    "parking_space_title": "Downtown Parking Spot"
  },
  "booking_id": 1,
  "payment_id": null,
  "is_read": true,
  "created_at": "2024-01-01T00:00:00Z",
  "read_at": "2024-01-01T00:05:00Z"
}
```

#### POST /api/notifications/mark-all-read

Mark all notifications as read for the authenticated user.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "message": "Marked 5 notifications as read"
}
```

#### DELETE /api/notifications/{notification_id}

Delete a notification.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "message": "Notification deleted successfully"
}
```

---

### Reminders

#### POST /api/admin/schedule-reminders

Schedule booking reminders (to be called periodically).

**Response:**

```json
{
  "message": "Booking reminders scheduled successfully"
}
```

#### POST /api/admin/process-periodic-reminders

Process periodic reminders (to be called every 30 minutes).

**Response:**

```json
{
  "message": "Processed periodic reminders successfully",
  "notifications_sent": 5
}
```

#### POST /api/admin/schedule-start-reminders

Start periodic reminders for bookings that are starting.

**Response:**

```json
{
  "message": "Booking start reminders scheduled successfully"
}
```

#### GET /api/admin/my-active-reminders

Get active reminders for the logged-in user.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "active_reminders": [
    {
      "id": 1,
      "booking_id": 1,
      "start_time": "2024-01-01T09:00:00Z",
      "end_time": "2024-01-01T17:00:00Z",
      "last_reminder_sent": "2024-01-01T08:30:00Z",
      "reminder_interval_minutes": 30,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /api/admin/stop-reminder/{booking_id}

Stop reminders for a specific booking.

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
{
  "message": "Reminder stopped successfully"
}
```

---

### Admin

#### GET /api/admin/users

List all users (admin only).

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### PUT /api/admin/users/{user_id}

Update user information (admin only).

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "role": "admin",
  "is_active": true
}
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "John Doe",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/admin/listings/{parking_id}/status

Update parking space listing status (admin only).

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Query Parameters:**

- `status` (string, required): New status
- `is_active` (bool, optional): Active status

**Response:**

```json
{
  "id": 1,
  "title": "Downtown Parking Spot",
  "description": "Secure parking in downtown area",
  "photos": ["https://example.com/photo1.jpg"],
  "price_per_hour": 5.5,
  "rules": "No overnight parking",
  "address": "123 Main St, City",
  "latitude": 40.7128,
  "longitude": -74.006,
  "is_active": true,
  "status": "approved",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/admin/issue-reports

List all issue reports (admin only).

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Response:**

```json
[
  {
    "id": 1,
    "created_by_user_id": 1,
    "booking_id": 1,
    "parking_space_id": 1,
    "subject": "Parking space not available",
    "description": "The parking space was occupied when I arrived",
    "status": "open",
    "admin_notes": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### PUT /api/admin/issue-reports/{issue_report_id}

Update issue report status (admin only).

**Headers:**

- `Authorization: Bearer <FIREBASE_ID_TOKEN>`

**Body:**

```json
{
  "status": "resolved",
  "admin_notes": "Issue has been resolved by contacting the parking owner"
}
```

**Response:**

```json
{
  "id": 1,
  "created_by_user_id": 1,
  "booking_id": 1,
  "parking_space_id": 1,
  "subject": "Parking space not available",
  "description": "The parking space was occupied when I arrived",
  "status": "resolved",
  "admin_notes": "Issue has been resolved by contacting the parking owner",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Error Codes

| Code | Description                          |
| ---- | ------------------------------------ |
| 200  | Success                              |
| 400  | Bad Request (invalid data)           |
| 401  | Unauthorized (invalid/missing token) |
| 403  | Forbidden (insufficient permissions) |
| 404  | Not Found                            |
| 409  | Conflict (resource not available)    |
| 422  | Validation Error                     |
| 500  | Internal Server Error                |

## Usage Examples

### JavaScript/Fetch

```javascript
const token = "YOUR_FIREBASE_ID_TOKEN";

// Get user profile
const response = await fetch("http://127.0.0.1:8000/api/users/me", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

const user = await response.json();
console.log(user);

// Create a booking
const bookingResponse = await fetch("http://127.0.0.1:8000/api/bookings/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    parking_space_id: 1,
    start_time: "2024-01-01T09:00:00Z",
    end_time: "2024-01-01T17:00:00Z",
  }),
});

const booking = await bookingResponse.json();
console.log(booking);
```

### Python/Requests

```python
import requests

token = "YOUR_FIREBASE_ID_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# Verify token
response = requests.post(
    "http://127.0.0.1:8000/api/auth/verify-token",
    headers=headers
)
print(response.json())

# Search for parking
search_params = {
    "lat": 40.7128,
    "lng": -74.0060,
    "radius_m": 1000,
    "start_time": "2024-01-01T09:00:00Z",
    "end_time": "2024-01-01T17:00:00Z"
}

response = requests.get(
    "http://127.0.0.1:8000/api/parking/search",
    params=search_params
)
print(response.json())
```

### cURL

```bash
# Health check
curl http://127.0.0.1:8000/health

# Get user profile
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/users/me

# Create a parking space
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Parking Spot",
    "description": "A great parking spot",
    "price_per_hour": 5.0,
    "address": "123 Main St",
    "latitude": 40.7128,
    "longitude": -74.0060
  }' \
  http://127.0.0.1:8000/api/parking/

# Search for parking
curl "http://127.0.0.1:8000/api/parking/search?lat=40.7128&lng=-74.0060&radius_m=1000"
```

## Swagger/OpenAPI

Interactive documentation is available at:

- **Development**: http://127.0.0.1:8000/docs
- **Production**: https://api.heirsprivpark.com/docs
