# Parking Management API

This document describes the Parking Management HTTP API provided by the backend. It covers endpoints for managing parking spaces, uploading photos, and handling availability windows.

All endpoints are mounted under the `/parking` prefix.

## Authentication

- Most endpoints require authentication via a Bearer token sent in the `Authorization` header:

  Authorization: Bearer <token>

- If the token is missing or invalid, requests will fail with an authentication error (401) or a token verification error returned by the auth dependency.

## High-level contract

- Inputs: JSON request bodies for create/update operations, multipart/form-data for photo uploads, and path parameters for identifying resources.
- Outputs: JSON objects matching the Pydantic schemas (see "Schemas" section). Successful mutating operations typically return the created/updated resource or `{"ok": true}` for deletions.
- Error modes: 401 Unauthorized (missing/invalid token), 403 Forbidden (authenticated but not resource owner), 404 Not Found (resource doesn't exist or not accessible), 422 Unprocessable Entity (validation errors).

## Schemas

The API uses these main request/response shapes (Pydantic model names shown):

- AvailabilityCreate

  - Fields: `start` , `end`

- AvailabilityOut

  - Fields: `id` (int), `start` (datetime), `end` (datetime)

- ParkingSpaceCreate / ParkingSpaceUpdate

  - Fields:
    - `title` (string) — required for create
    - `description` (string | null)
    - `photos` (array[string] | null) — list of photo URLs (when creating/updating you may pass a list of URLs)
    - `price_per_hour` (float | null)
    - `rules` (string | null)
    - `address` (string | null)
    - `latitude` (float | null)
    - `longitude` (float | null)

- ParkingSpaceOut
  - Fields: `id` (int), `owner_id` (int), all fields from ParkingSpaceCreate, `availabilities` (array of AvailabilityOut | null)

Note: Internally the project stores `photos` as a comma-separated string in the database. The public API contract uses a list of strings for `photos`. The router code converts between those representations when creating/updating parking spaces and when appending uploaded photos.

## Booking & Payments (overview)

- `POST /bookings` — create a booking (requires availability). Body: `parking_space_id`, `start_time`, `end_time`. Returns booking with computed `total_amount`.
- `GET /bookings` — list current user's bookings.
- `GET /bookings/{id}` — get a specific booking (owner only).
- `DELETE /bookings/{id}` — cancel a non-confirmed booking.
- `POST /payments/create-checkout-session` — returns a Stripe Checkout URL for a booking. Body: `booking_id`, `success_url`, `cancel_url`.
- `POST /payments/webhook` — Stripe webhook endpoint to confirm payment and persist a `Payment` with receipt URL.

## Endpoints

1. Create parking space

   - Method: POST
   - Path: /parking/
   - Auth: Required (Authorization header)
   - Request body: `ParkingSpaceCreate` JSON
   - Response: `ParkingSpaceOut` (201/200)
   - Notes: If `photos` is provided as an array it will be stored internally as a comma-separated string.

   Example request body:

   {
   "title": "Covered driveway spot",
   "description": "Covered parking near elevator",
   "photos": ["https://cdn.example.com/img1.jpg"],
   "price_per_hour": 2.5,
   "rules": "No smoking",
   "address": "123 Main St",
   "latitude": 40.7128,
   "longitude": -74.0060
   }

2. List parking spaces (owner's spaces)

   - Method: GET
   - Path: /parking/
   - Auth: Required
   - Query: none
   - Response: array[`ParkingSpaceOut`]

   Notes: Returns parking spaces for the authenticated user (owner_id == current user).

3. Get one parking space
4. Admin listing moderation

   - Method: PUT
   - Path: /admin/listings/{parking_id}/status
   - Auth: Admin required
   - Body: form/query: `status` in [pending, approved, rejected], optional `is_active`
   - Response: `ParkingSpaceOut`

   - Method: GET
   - Path: /parking/{parking_id}
   - Auth: Required
   - Response: `ParkingSpaceOut` or 404 if the space does not exist or is not owned by the current user.

5. Update parking space

   - Method: PUT
   - Path: /parking/{parking_id}
   - Auth: Required
   - Request body: `ParkingSpaceUpdate` (partial updates allowed; only set fields are applied)
   - Response: `ParkingSpaceOut`
   - Notes: If `photos` is omitted it is left unchanged. If `photos` is provided it replaces the stored photo list (the code accepts an array and stores a CSV internally).

6. Delete parking space

   - Method: DELETE
   - Path: /parking/{parking_id}
   - Auth: Required
   - Response: {"ok": true}
   - Errors: 404 if not found or not owner.

7. Add availability for a parking space

   - Method: POST
   - Path: /parking/{parking_id}/availability
   - Auth: Required
   - Request body: `AvailabilityCreate` JSON
   - Response: `AvailabilityOut`
   - Errors: 404 if the parking space does not exist or is not owned by the user.

   Example request body:

   {
   "start": "2025-10-01T08:00:00+00:00",
   "end": "2025-10-01T18:00:00+00:00"
   }

8. List availabilities for a space (public read)

   - Method: GET
   - Path: /parking/{parking_id}/availability
   - Auth: Not required (public read allowed)
   - Response: array[`AvailabilityOut`]

9. Delete availability

   - Method: DELETE
   - Path: /parking/availability/{availability_id}
   - Auth: Required
   - Response: {"ok": true}
   - Authorization: The user must be the owner of the parking space that the availability belongs to. If not the owner, a 403 Forbidden is returned.

10. Upload a photo for a parking space

    - Method: POST
    - Path: /parking/{parking_id}/photos
    - Auth: Required
    - Content-Type: multipart/form-data
    - Form field: `file` — the file to upload
    - Response: {"url": "https://..."}
    - Behavior: The server uploads the file to S3 (using `app.core.storage.upload_fileobj_to_s3`) and appends the returned URL to the parking space's stored `photos` CSV. Returns the uploaded file URL.

    Example response:

    {
    "url": "https://s3.amazonaws.com/bucket/parks/abc123.jpg"
    }

## Validation, formats and tips

- Datetimes: Use RFC 3339 / ISO 8601 format with timezone (e.g., "2025-10-01T08:00:00+00:00"). The application stores datetimes with timezone-aware DateTime columns.
- Photos: When creating/updating a parking space you may pass `photos` as an array of URL strings. The backend persists photos as a single comma-separated string (DB column `photos`). The API surface expects/returns an array of strings.
- Coordinates: `latitude` and `longitude` are optional floats; pass both if you want geo-location support.
- Pricing: `price_per_hour` is a float.

## Errors and status codes

- 200 OK — Successful GET/PUT/POST responses that return resources.
- 201 Created — (not explicitly set but POST returns the created resource) — treated as success.
- 204 No Content — not used; deletions return {"ok": true}.
- 401 Unauthorized — missing/invalid Authorization header.
- 403 Forbidden — authenticated but not the owner (used e.g. when deleting an availability that belongs to another user's parking space).
- 404 Not Found — resource doesn't exist or not accessible by the caller.
- 422 Unprocessable Entity — validation errors (invalid payload or missing required fields).
