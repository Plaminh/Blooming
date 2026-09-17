# Quickstart: Auth and User Settings Validation

This guide provides steps to validate the auth and settings features end-to-end against the local backend.

## Prerequisites
- The FastAPI backend must be running.
- A database configured and migrated to the latest Alembic revision.
- `curl` or a similar HTTP client.

## Validation Steps

### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com", "password":"password123", "display_name":"Test User"}'
```
**Expected outcome**: A `201 Created` response containing the user profile and requiring email verification.
*Note: You will need to check the local Brevo test stub (or your inbox) for the verification link. Use the link to verify your email. The verification endpoint returns the `access_token`.*

### 2. Login (Verify credentials)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d 'username=test@example.com&password=password123'
```
**Expected outcome**: A `200 OK` response with a new access token.

### 3. Retrieve Profile
```bash
curl -X GET http://localhost:8000/api/v1/me \
     -H "Authorization: Bearer $TOKEN"
```
**Expected outcome**: A `200 OK` response showing the profile without password hashes.

### 4. Update Profile
```bash
curl -X PUT http://localhost:8000/api/v1/me \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"display_name":"Updated User"}'
```
**Expected outcome**: A `200 OK` response with the updated display name.

### 5. Retrieve Settings (Verify Defaults)
```bash
curl -X GET http://localhost:8000/api/v1/me/settings \
     -H "Authorization: Bearer $TOKEN"
```
**Expected outcome**: A `200 OK` response showing the default values (e.g. `default_focus_minutes` = 25).

### 6. Update Settings
```bash
curl -X PUT http://localhost:8000/api/v1/me/settings \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"default_focus_minutes":50, "widget_visibility":false}'
```
**Expected outcome**: A `200 OK` response showing the updated fields while other fields remain at their defaults.

### 7. Unauthorized Access Check
```bash
curl -X GET http://localhost:8000/api/v1/me
```
**Expected outcome**: A `401 Unauthorized` error since the Bearer token is omitted.

