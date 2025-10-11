# Notification System - Heirs PrivPark

## Overview

The basic notification system has been implemented to provide automatic notifications to users regarding their bookings and payments, including periodic reminders every 30 minutes while a booking is in progress.

## Implemented Features

### Notification Types

1. **Booking Confirmation** (`booking_confirmation`)

   - Sent when a booking is created
   - Contains booking details (parking, times, amount)

2. **Payment Confirmation** (`payment_confirmation`)

   - Sent when a payment is successful
   - Contains payment details and receipt link

3. **Booking Reminder** (`booking_reminder`)

   - Sent 1 hour before booking start
   - Can be scheduled via dedicated endpoint

4. **Booking End Reminder** (`booking_end_reminder`) ⭐ **NEW**

   - Sent every 30 minutes while a booking is in progress
   - Reminds user of imminent booking end
   - Contains remaining time in minutes

5. **Booking Cancellation** (`booking_cancelled`)

   - Sent when a booking is cancelled
   - Contains cancellation details

6. **Payment Failure** (`payment_failed`)
   - Sent when a payment fails
   - Contains error details

## Database Structure

### `notifications` Table

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type notificationtype NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data TEXT, -- JSON string for additional data
    booking_id INTEGER REFERENCES bookings(id),
    payment_id INTEGER REFERENCES payments(id),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);
```

### `active_reminders` Table ⭐ **NEW**

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

### `notificationtype` Enum

```sql
CREATE TYPE notificationtype AS ENUM (
    'booking_confirmation',
    'payment_confirmation',
    'booking_reminder',
    'booking_end_reminder',  -- ⭐ NEW
    'booking_cancelled',
    'payment_failed'
);
```

## API Endpoints

### User Notifications

- `GET /notifications/` - Get user notifications
- `GET /notifications/stats` - Notification statistics
- `GET /notifications/{id}` - Get specific notification
- `PATCH /notifications/{id}/read` - Mark as read
- `POST /notifications/mark-all-read` - Mark all as read
- `DELETE /notifications/{id}` - Delete notification

### Administration and Reminders ⭐ **NEW**

- `POST /admin/schedule-reminders` - Schedule booking start reminders
- `POST /admin/process-periodic-reminders` - Process periodic reminders (30min)
- `POST /admin/schedule-start-reminders` - Start reminders for ongoing bookings
- `GET /admin/my-active-reminders` - Get user's active reminders
- `POST /admin/stop-reminder/{booking_id}` - Stop reminders for a booking

## Usage

### Automatic Integration

Notifications are automatically created during the following events:

1. **Booking Creation** - Confirmation notification
2. **Successful Payment** - Payment confirmation notification
3. **Booking Cancellation** - Cancellation notification

### Periodic Reminder Scheduling ⭐ **NEW**

The periodic reminder system works in several steps:

1. **Automatic Start**: When a booking begins, periodic reminders are automatically started
2. **Periodic Processing**: An endpoint must be called every 30 minutes to process reminders
3. **Automatic Cleanup**: Expired reminders are automatically cleaned up

#### Recommended Configuration

```bash
# Cron job to process reminders every 30 minutes
*/30 * * * * curl -X POST http://your-api/admin/process-periodic-reminders

# Cron job to start reminders for bookings that begin (every 5 minutes)
*/5 * * * * curl -X POST http://your-api/admin/schedule-start-reminders

# Cron job for booking start reminders (every hour)
0 * * * * curl -X POST http://your-api/admin/schedule-reminders
```

### Usage Example

```python
from app.services.notification_service import NotificationService

# Create a custom notification
NotificationService.create_booking_confirmation_notification(
    db, booking, user
)

# Start periodic reminders for a booking
NotificationService.start_booking_end_reminders(db, booking, user)

# Process all pending reminders
notifications_sent = NotificationService.process_periodic_reminders(db)

# Stop reminders for a booking
NotificationService.stop_booking_end_reminders(db, booking)
```

## Migration

To apply changes to the database:

```bash
cd backend
alembic upgrade head
```

## Testing

An improved test script is provided to verify functionality:

```bash
python test_notifications.py
```

The script now tests:

- ✅ Booking confirmation notifications
- ✅ Starting periodic reminders
- ✅ Sending reminders every 30 minutes
- ✅ Stopping reminders
- ✅ Cleaning up expired reminders
- ✅ Notification statistics

## File Structure

```
backend/
├── app/
│   ├── db/
│   │   ├── models/
│   │   │   ├── notification.py          # Notification Model
│   │   │   └── active_reminder.py      # ⭐ NEW: ActiveReminder Model
│   │   └── repositories/
│   │       ├── notification_repo.py    # Repository for notifications
│   │       └── active_reminder_repo.py # ⭐ NEW: Repository for active reminders
│   ├── schemas/
│   │   └── notification.py              # Pydantic Schemas
│   ├── services/
│   │   └── notification_service.py     # Notification management service
│   └── api/
│       ├── routes_notifications.py     # Notification API routes
│       └── routes_reminders.py         # Routes for reminders (enhanced)
├── alembic/versions/
│   ├── 0004_add_notifications.py       # Notifications migration
│   └── 0005_add_active_reminders.py   # ⭐ NEW: Active reminders migration
└── test_notifications.py              # Test script (enhanced)
```

## Periodic Reminders Functionality ⭐ **NEW**

### Booking Lifecycle with Reminders

1. **Booking Created** → Confirmation notification
2. **Payment Successful** → Payment confirmation notification
3. **1 hour before start** → Booking start reminder
4. **Booking Start** → Automatic start of periodic reminders
5. **During booking** → Reminder every 30 minutes
6. **Booking End** → Automatic stop of reminders

### Intelligent Reminder Management

- **Avoids Duplicates**: Checks that a reminder hasn't already been sent in the interval
- **Automatic Cleanup**: Removes reminders for completed bookings
- **Error Handling**: Continues processing even if a notification fails
- **Statistics**: Returns the number of notifications sent

## Notification Examples

### Booking Confirmation

```json
{
  "type": "booking_confirmation",
  "title": "Booking Confirmed",
  "message": "Your booking for parking #123 has been created successfully. Start: 15/01/2024 at 14:00",
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

### Booking End Reminder

```json
{
  "type": "booking_end_reminder",
  "title": "Booking End Reminder",
  "message": "Your booking for parking #123 ends in 30 minutes. Expected end: 15/01/2024 at 16:00",
  "data": {
    "booking_id": 456,
    "parking_space_id": 123,
    "end_time": "2024-01-15T16:00:00Z",
    "minutes_remaining": 30,
    "reminder_type": "end_reminder"
  }
}
```

### Payment Confirmation

```json
{
  "type": "payment_confirmation",
  "title": "Payment Confirmed",
  "message": "Your payment of 20.0 USD has been processed successfully. Your booking is now confirmed.",
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

## Error Handling

The notification system is designed to be robust:

- **Non-blocking Notifications**: Notification errors don't affect main operations
- **Error Logging**: All errors are logged for debugging
- **Automatic Retry**: Possibility to implement a retry system
- **Fallback**: In case of failure, data is preserved for later retry

## Monitoring and Statistics

### Monitoring Endpoints

- `GET /notifications/stats` - Statistics per user
- `GET /admin/my-active-reminders` - Active reminders per user

### Available Metrics

- Total number of notifications
- Number of unread notifications
- Distribution by notification type
- Number of active reminders
- Number of notifications sent per processing

## Security

- **Authentication Required**: All user endpoints require authentication
- **Data Isolation**: Users can only access their own notifications
- **Data Validation**: All input data is validated
- **CSRF Protection**: Endpoints use appropriate authentication tokens

## Performance

### Implemented Optimizations

- **Indexes on Frequently Used Columns**: `user_id`, `booking_id`, `created_at`
- **Pagination**: Default limit of 50 notifications with possibility to increase
- **Automatic Cleanup**: Removal of expired reminders
- **Optimized Queries**: Use of efficient joins

### Recommendations

- **Archiving**: Consider archiving old notifications
- **Cache**: Implement Redis cache for frequent statistics
- **Batch Processing**: Process notifications in batches for large volumes

## Next Steps

To extend the notification system:

1. **Push Notifications** - Integration with Firebase Cloud Messaging
2. **Email Notifications** - Automatic email sending
3. **SMS Notifications** - Integration with SMS service
4. **User Preferences** - Allow users to configure their preferences
5. **Templates** - Message template system
6. **History** - Archiving of old notifications
7. **Analytics** - Notification engagement statistics
8. **Custom Reminders** - Allow users to define their own intervals
9. **Geolocated Notifications** - Reminders based on parking proximity
10. **Multi-language Notifications** - Support for multiple languages

## Support and Maintenance

### Logs to Monitor

- Notification creation errors
- Periodic reminder sending failures
- Expired reminder cleanup problems
- Authentication errors on endpoints

### Regular Maintenance

- Check cron jobs
- Monitor query performance
- Clean up old notifications if necessary
- Update message templates

## Conclusion

The Heirs PrivPark notification system provides a complete solution for informing users about the status of their bookings and payments. With periodic reminders every 30 minutes, users are always informed of the remaining time of their booking, thus improving their user experience and reducing the risks of time overruns.
