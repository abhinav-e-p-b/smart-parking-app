# Smart Parking API Documentation

## Base URL

\`\`\`
https://api.smartpark.app/
\`\`\`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

\`\`\`
Authorization: Bearer <your_token>
\`\`\`

## Endpoints

### 1. Authentication

#### Register User

**POST** `/api/auth/register`

Request:
\`\`\`json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
\`\`\`

Response:
\`\`\`json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
\`\`\`

#### Login

**POST** `/api/auth/login`

Request:
\`\`\`json
{
  "username": "john_doe",
  "password": "secure_password"
}
\`\`\`

Response:
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": 1
}
\`\`\`

### 2. Parking Predictions

#### Get Availability Prediction

**POST** `/api/predict-availability`

Request:
\`\`\`json
{
  "time_of_day": 14,
  "day_of_week": 3,
  "location_id": 1,
  "historical_occupancy_rate": 65.5,
  "previous_duration_hours": 2.5,
  "traffic_density": "Medium"
}
\`\`\`

Response:
\`\`\`json
{
  "location_id": 1,
  "prediction": "available",
  "availability_probability": 0.78,
  "confidence": 78.0,
  "timestamp": "2024-01-15T14:30:00"
}
\`\`\`

**Parameters:**
- `time_of_day` (int): Hour of day (0-23)
- `day_of_week` (int): Day of week (0-6, where 0=Monday)
- `location_id` (int): Parking area ID
- `historical_occupancy_rate` (float): Historical occupancy percentage (0-100)
- `previous_duration_hours` (float): Average previous parking duration (0.5-8)
- `traffic_density` (string): Current traffic level (Low, Medium, High)

#### Get Nearby Parkings

**POST** `/api/nearby-parkings`

Request:
\`\`\`json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius_km": 5.0
}
\`\`\`

Response:
\`\`\`json
{
  "recommendations": [
    {
      "spot_id": 1,
      "name": "Downtown Garage A",
      "latitude": 40.7130,
      "longitude": -74.0058,
      "availability_probability": 0.85,
      "distance_km": 0.5,
      "traffic_level": "Low",
      "price_per_hour": 5.50,
      "available_slots": 45,
      "total_slots": 150,
      "confidence": 85.0,
      "scores": {
        "availability": 0.850,
        "distance": 0.900,
        "traffic": 1.000,
        "price": 0.700,
        "final": 0.845
      }
    }
  ]
}
\`\`\`

### 3. Bookings

#### Create Booking

**POST** `/api/bookings`

Headers: `Authorization: Bearer <token>`

Request:
\`\`\`json
{
  "parking_slot_id": 123,
  "check_in_time": "2024-01-15T14:30:00"
}
\`\`\`

Response:
\`\`\`json
{
  "id": 1,
  "user_id": 1,
  "parking_slot_id": 123,
  "check_in_time": "2024-01-15T14:30:00",
  "check_out_time": null,
  "status": "active",
  "duration_hours": null,
  "amount_paid": null,
  "created_at": "2024-01-15T14:30:00"
}
\`\`\`

#### Get Booking Details

**GET** `/api/bookings/{booking_id}`

Headers: `Authorization: Bearer <token>`

Response: Same as Create Booking response

#### Checkout Parking

**POST** `/api/bookings/{booking_id}/checkout`

Headers: `Authorization: Bearer <token>`

Response:
\`\`\`json
{
  "booking_id": 1,
  "duration_hours": 2.5,
  "amount_paid": 13.75,
  "status": "completed"
}
\`\`\`

### 4. Parking Areas

#### Get All Parking Areas

**GET** `/api/parking-areas?skip=0&limit=100`

Response:
\`\`\`json
[
  {
    "id": 1,
    "name": "Downtown Garage A",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "total_slots": 150,
    "address": "123 Main St, NYC",
    "price_per_hour": 5.50
  }
]
\`\`\`

#### Get Specific Parking Area

**GET** `/api/parking-areas/{area_id}`

Response: Single parking area object

## Error Responses

### 400 Bad Request
\`\`\`json
{
  "detail": "Invalid request parameters"
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "detail": "Invalid authentication credentials"
}
\`\`\`

### 404 Not Found
\`\`\`json
{
  "detail": "Resource not found"
}
\`\`\`

### 500 Internal Server Error
\`\`\`json
{
  "detail": "Internal server error"
}
\`\`\`

## Rate Limiting

- Default: 100 requests per 15 minutes per IP
- Authenticated users: 1000 requests per 15 minutes

## Response Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Example Usage

### Complete Workflow

1. **Register/Login**
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"password"}'
\`\`\`

2. **Get Recommendations**
\`\`\`bash
curl -X POST http://localhost:8000/api/nearby-parkings \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius_km": 5.0
  }'
\`\`\`

3. **Make Booking**
\`\`\`bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parking_slot_id": 123,
    "check_in_time": "2024-01-15T14:30:00"
  }'
\`\`\`

4. **Checkout**
\`\`\`bash
curl -X POST http://localhost:8000/api/bookings/1/checkout \
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

## Pagination

Endpoints that return lists support pagination:

- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100, max: 1000)

Example:
\`\`\`bash
GET /api/parking-areas?skip=0&limit=50
\`\`\`

## Filtering

Some endpoints support filtering:

\`\`\`bash
GET /api/bookings?status=completed&user_id=1
\`\`\`

## Webhooks (Coming Soon)

Subscribe to real-time parking availability updates.

## Support

For API support, contact: api-support@smartpark.app
