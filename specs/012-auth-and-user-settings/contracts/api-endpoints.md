# API Contracts: Auth and User Settings

All endpoints are prefixed with `/api/v1`.

## 1. Registration

**POST** `/auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "display_name": "Alice"
}
```

**Response (201 Created)**:
```json
{
  "email": "user@example.com",
  "verification_required": true
}
```

**Errors**:
- `400 Bad Request`: Validation failure (e.g. invalid email).
- `409 Conflict`: Email already registered.

---

## 2. Login

**POST** `/auth/login`

**Request Body** (Can be JSON or `OAuth2PasswordRequestForm` as per standard FastAPI):
Using standard OAuth2 form:
```text
username=user@example.com&password=securepassword123
```

**Response (200 OK)**:
```json
{
  "access_token": "jwt.string.here",
  "token_type": "bearer"
}
```

**Errors**:
- `401 Unauthorized`: Incorrect username or password. (Generic message).
- `403 Forbidden`: `EMAIL_NOT_VERIFIED` or `Account is not active`.

---

## 3. Retrieve Profile

**GET** `/me`

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "Alice",
  "created_at": "2026-09-16T12:00:00Z"
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid token.

---

## 4. Update Profile

**PUT** `/me`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (Editable fields only):
```json
{
  "display_name": "Alice Wonderland"
}
```
*Note: Any protected fields submitted must be rejected or silently ignored.*

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "Alice Wonderland",
  "created_at": "2026-09-16T12:00:00Z"
}
```

---

## 5. Retrieve Settings

**GET** `/me/settings`

**Headers**: `Authorization: Bearer <token>`

**Response (200 OK)**:
```json
{
  "timezone": "UTC",
  "default_focus_minutes": 25,
  "default_break_minutes": 5,
  "quiet_hours_enabled": false,
  "quiet_hours_start": null,
  "quiet_hours_end": null,
  "mr_bloom_display_name": "Mr. Bloom",
  "widget_visibility": true,
  "widget_always_on_top": false,
  "launch_on_startup": false,
  "weather_enabled": false,
  "weather_location": null
}
```

---

## 6. Update Settings

**PUT** `/me/settings`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (Partial updates supported; omitted fields remain unchanged):
```json
{
  "default_focus_minutes": 50,
  "default_break_minutes": 10,
  "widget_always_on_top": true
}
```

**Response (200 OK)**:
```json
{
  "timezone": "UTC",
  "default_focus_minutes": 50,
  "default_break_minutes": 10,
  "quiet_hours_enabled": false,
  "quiet_hours_start": null,
  "quiet_hours_end": null,
  "mr_bloom_display_name": "Mr. Bloom",
  "widget_visibility": true,
  "widget_always_on_top": true,
  "launch_on_startup": false,
  "weather_enabled": false,
  "weather_location": null
}
```

**Errors**:
- `422 Unprocessable Entity`: Validation failure (e.g. `default_focus_minutes` > 720).

---

## 7. Verify Email

**POST** `/auth/verify-email`

**Request Body**:
```json
{
  "token": "raw-token-string"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "jwt.string.here",
  "token_type": "bearer"
}
```

**Errors**:
- `400 Bad Request`: Invalid or expired token.

---

## 8. Resend Verification Email

**POST** `/auth/resend-verification`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK)**:
```json
{
  "message": "If the account exists, a verification email has been resent."
}
```



