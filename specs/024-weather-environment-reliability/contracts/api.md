# Weather and Location API Contracts

## `GET /api/weather/search`

Searches for location candidates via geocoding.

**Query Parameters:**
- `q`: `string` (Required, min 2 chars) - The location query.

**Response:** `200 OK`
```json
{
  "candidates": [
    {
      "name": "London, United Kingdom",
      "lat": 51.51,
      "lon": -0.13
    }
  ]
}
```
*Note: Coordinates in response must already be rounded to 2 decimal places.*

## `GET /api/weather/current`

Retrieves the current weather status based on the user's saved location.

**Response:** `200 OK`
```json
{
  "condition": "CLEAR", 
  "status": "OK", 
  "updated_at": "2026-09-19T14:30:00Z"
}
```
*Note: `condition` can be one of: `CLEAR`, `CLOUDY`, `OVERCAST`, `RAIN`, `THUNDERSTORM`. `status` can be one of: `OK`, `STALE`, `UNAVAILABLE`, `DISABLED`.*

## `PUT /api/settings/weather` (Update to existing endpoint)

Updates user weather and season settings.

**Request Body:**
```json
{
  "weather_location_name": "London, United Kingdom",
  "weather_lat": 51.51,
  "weather_lon": -0.13,
  "scene_season": "AUTO"
}
```

**Response:** `200 OK`
(Returns the updated UserSettings object)
