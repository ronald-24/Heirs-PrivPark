# Admin Panel (Back Office) 🛠️

**Complete documentation of the administration panel for Heirs-PrivPark**

## 📋 Overview

The administration panel allows administrators to efficiently manage the private parking rental platform. It includes user management, listing moderation, and issue report resolution.

## 🔐 Authentication and Authorization

### Prerequisites

- **Required Role**: `admin` (defined in the `role` field of the `users` table)
- **Authentication**: Valid Firebase token via `Authorization: Bearer <token>` header
- **Verification**: All admin routes use `require_role("admin", user.role)`

### Create an Admin User

```sql
-- Via direct SQL
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';

-- Or via API (if you already have an admin)
PUT /admin/users/{user_id}
{
  "role": "admin"
}
```

## 👥 User Management

### 1. List All Users

**Endpoint**: `GET /admin/users`

**Response**:

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

**Usage**:

- View all registered users
- Identify inactive accounts
- Monitor user activity

### 2. Modify a User

**Endpoint**: `PUT /admin/users/{user_id}`

**Body**:

```json
{
  "role": "admin", // Optional: "user" or "admin"
  "is_active": false // Optional: true/false
}
```

**Use Cases**:

- **Promote a User**: `role: "admin"`
- **Suspend an Account**: `is_active: false`
- **Reactivate an Account**: `is_active: true`

**Example**:

```bash
curl -X PUT "http://localhost:8000/admin/users/123" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "is_active": true}'
```

## 🅿️ Listing Moderation

### 1. Approve/Reject a Listing

**Endpoint**: `PUT /admin/listings/{parking_id}/status`

**Parameters**:

- `status` (required): `"pending"`, `"approved"`, `"rejected"`
- `is_active` (optional): `true`/`false`

**Examples**:

**Approve a Listing**:

```bash
curl -X PUT "http://localhost:8000/admin/listings/456/status?status=approved" \
  -H "Authorization: Bearer <admin_token>"
```

**Reject a Listing**:

```bash
curl -X PUT "http://localhost:8000/admin/listings/456/status?status=rejected" \
  -H "Authorization: Bearer <admin_token>"
```

**Temporarily Disable**:

```bash
curl -X PUT "http://localhost:8000/admin/listings/456/status?status=approved&is_active=false" \
  -H "Authorization: Bearer <admin_token>"
```

### 2. Listing States

| State      | Description        | Visibility |
| ---------- | ------------------ | ---------- |
| `pending`  | Pending moderation | ❌ Hidden  |
| `approved` | Approved by admin  | ✅ Visible |
| `rejected` | Rejected by admin  | ❌ Hidden  |

**Filtering Logic**:

- Only listings with `status = "approved"` AND `is_active = true` appear in searches
- Owners can always see their listings, even rejected ones

## 🚨 Issue Report Management

### 1. List All Issue Reports

**Endpoint**: `GET /admin/issue-reports`

**Response**:

```json
[
  {
    "id": 1,
    "created_by_user_id": 123,
    "booking_id": 456,
    "parking_space_id": 789,
    "subject": "Parking space in poor condition",
    "description": "The space is very narrow and the floor is broken...",
    "status": "open",
    "admin_notes": null,
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  }
]
```

### 2. Process an Issue Report

**Endpoint**: `PUT /admin/issue-reports/{issue_report_id}`

**Body**:

```json
{
  "status": "resolved", // "open", "in_review", "resolved", "dismissed"
  "admin_notes": "50% refund granted. Owner contacted to improve signage."
}
```

**Issue Report States**:

| State       | Description      | Required Action      |
| ----------- | ---------------- | -------------------- |
| `open`      | New issue report | Examine the problem  |
| `in_review` | Under review     | Contact parties      |
| `resolved`  | Resolved         | Close the case       |
| `dismissed` | Rejected         | Justify the decision |

### 3. Resolution Examples

**Issue Resolved with Refund**:

```json
{
  "status": "resolved",
  "admin_notes": "Problem confirmed. 50% refund granted (7.50€). Owner warned to improve quality."
}
```

**Issue Dismissed**:

```json
{
  "status": "dismissed",
  "admin_notes": "Photos verified - listing matches reality. No action required."
}
```

## 📊 Admin Dashboard

### Key Metrics to Monitor

```python
# Example queries for the dashboard
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

## 🔄 Moderation Workflow

### 1. New Listing Created

```
Owner creates listing → status: "pending" → Admin receives notification → Admin reviews → Approves/Rejects
```

### 2. Issue Report Created

```
User reports issue → status: "open" → Admin reviews → Sets to "in_review" → Resolves or Dismisses
```

### 3. Preventive Actions

- **Monitoring**: Regularly check pending listings
- **Responsiveness**: Process issue reports within 24h
- **Communication**: Inform owners of decisions

## 🛡️ Security Best Practices

### 1. Permission Verification

```python
# Always verify admin role
user, _ = verify_bearer_token_and_get_user(authorization=Authorization, db=db)
require_role("admin", user.role)
```

### 2. Data Validation

- Verify resource existence before modification
- Validate authorized statuses
- Log all admin actions

### 3. Audit Trail

```python
# Example admin action log
admin_action_log = {
    "admin_id": user.id,
    "action": "approve_listing",
    "target_id": parking_id,
    "timestamp": datetime.now(),
    "details": {"status": "approved"}
}
```

## 📱 Recommended User Interface

### Main Sections

1. **Dashboard**: Overview of metrics
2. **Users**: Account list and management
3. **Listings**: Parking moderation
4. **Issue Reports**: Problem resolution
5. **Statistics**: Reports and analytics

### UX Features

- **Filters**: By status, date, user
- **Search**: By ID, email, subject
- **Bulk Actions**: Multiple selection
- **Notifications**: Alerts for new actions

## 🚀 Deployment and Configuration

### Environment Variables

```bash
# Default admin (optional)
DEFAULT_ADMIN_EMAIL=admin@heirsprivpark.com

# Admin notifications
ADMIN_NOTIFICATION_EMAIL=admin@heirsprivpark.com
```

### Database Migration

```bash
# Apply migrations
cd backend
alembic upgrade head

# Check new tables
psql -d privpark -c "\dt"
```

## 🔧 Maintenance and Monitoring

### Regular Tasks

- **Daily**: Review new issue reports
- **Weekly**: Analyze usage metrics
- **Monthly**: Clean up old data

### Recommended Alerts

- New urgent issue report
- Listing pending > 24h
- Suspended user
- Technical problem detected
