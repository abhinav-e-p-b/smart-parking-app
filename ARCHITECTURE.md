# Smart Parking Application - System Architecture

## Overview
The Smart Parking Application predicts parking availability using Machine Learning and provides real-time recommendations to users through a web/mobile interface.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│  (Next.js Web App - Mobile Responsive)                         │
│  - Map View with Parking Pins                                  │
│  - Parking Details & Predictions                               │
│  - User Authentication                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (REST API)
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                           │
│  (FastAPI/Python)                                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ API Routes                                              │  │
│  │ - /api/predict-availability (POST)                      │  │
│  │ - /api/nearby-parkings (GET)                            │  │
│  │ - /api/parking-details/<id> (GET)                       │  │
│  │ - /api/book-parking (POST)                              │  │
│  │ - /api/history (GET)                                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ ML Model Pipeline                                       │  │
│  │ - Feature Engineering                                   │  │
│  │ - Model Inference (Random Forest)                       │  │
│  │ - Recommendation Scoring                                │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Computer Vision Module (Optional)                       │  │
│  │ - Image Processing (OpenCV)                             │  │
│  │ - YOLO/MobileNet Detection                              │  │
│  │ - Slot Availability Detection                           │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (SQL/ORM)
┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                            │
│  (PostgreSQL / Supabase)                                        │
│  - Users Table                                                  │
│  - Parking Areas Table                                          │
│  - Parking Slots Table                                          │
│  - Bookings Table                                               │
│  - Parking History Table                                        │
│  - ML Training Data Table                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Frontend (Next.js)
- Real-time map view with parking locations
- Availability predictions with confidence scores
- User authentication and profile management
- Booking and history tracking

### 2. Backend (FastAPI)
- RESTful API endpoints for parking predictions
- ML model inference pipeline
- Database operations and queries
- Computer vision API integration

### 3. ML Pipeline
- **Data Preparation**: Time, location, occupancy history features
- **Model Types**:
  - Baseline: Logistic Regression
  - Production: Random Forest
  - Optional: XGBoost
- **Output**: Probability score (0-1) for availability

### 4. Database Schema
- Normalized PostgreSQL structure
- Support for real-time updates
- Historical data for model training

### 5. Recommendation Algorithm
Weighted scoring formula:
```
Score = (0.4 × Availability%) + (0.3 × Distance_Weight) + (0.2 × TrafficWeight) + (0.1 × UserPreference)
```

## Technology Stack
- **Frontend**: Next.js 16, React, Tailwind CSS, Leaflet/Google Maps API
- **Backend**: FastAPI, Python 3.9+
- **ML**: scikit-learn, pandas, numpy, joblib
- **Database**: PostgreSQL with Supabase
- **Deployment**: Vercel (Frontend), Railway/Render (Backend)
- **CV**: OpenCV, YOLO/MobileNet

## Data Flow

1. **User Input**: Destination address entered via map interface
2. **Location Processing**: Geocode address → Get nearby parking areas
3. **Feature Extraction**: Extract time, location, traffic features
4. **ML Prediction**: Pass features to trained model → Get availability probability
5. **Scoring & Ranking**: Apply recommendation formula → Rank parking spots
6. **Display Results**: Show ranked options with details to user
7. **Booking/History**: Record user action → Update training data

## Security Considerations
- JWT authentication for user sessions
- SQL parameterized queries (SQLAlchemy ORM)
- API rate limiting and validation
- Environment variables for sensitive credentials
- CORS configuration for frontend access
