"""
FastAPI Backend for Smart Parking Application
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from database import SessionLocal, get_db, init_db
from models import User, ParkingArea, ParkingSlot, Booking, ParkingHistory, MLTrainingData
from schemas import (
    UserCreate, UserResponse, ParkingAreaResponse, ParkingSlotResponse,
    PredictionRequest, PredictionResponse, NearbyParkingRequest,
    ParkingRecommendation, BookingCreate, BookingResponse
)
from auth import hash_password, verify_password, create_access_token, get_current_user
from ml_model import ParkingAvailabilityModel
from recommendation_engine import ParkingSpot, RecommendationEngine

load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Smart Parking API",
    description="ML-powered parking prediction and recommendation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML model
try:
    model = ParkingAvailabilityModel.load('models/random_forest_model.pkl')
    recommendation_engine = RecommendationEngine(max_distance_km=5.0)
except Exception as e:
    print(f"Warning: Could not load ML model: {e}")
    model = None

# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")

# Authentication Bearer
security = HTTPBearer()

# ============ Authentication Endpoints ============

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/auth/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """Login user and return access token"""
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id}


# ============ Prediction Endpoints ============

@app.post("/api/predict-availability", response_model=PredictionResponse)
async def predict_availability(request: PredictionRequest):
    """Predict parking availability"""
    if not model:
        raise HTTPException(status_code=500, detail="ML model not loaded")
    
    try:
        data = pd.DataFrame([{
            'time_of_day': request.time_of_day,
            'day_of_week': request.day_of_week,
            'location_id': request.location_id,
            'historical_occupancy_rate': request.historical_occupancy_rate,
            'previous_duration_hours': request.previous_duration_hours,
            'traffic_density': request.traffic_density
        }])
        
        predictions, probabilities = model.predict(data)
        availability_prob = float(probabilities[0])
        
        return PredictionResponse(
            location_id=request.location_id,
            prediction="available" if predictions[0] else "occupied",
            availability_probability=availability_prob,
            confidence=round(availability_prob * 100, 1),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


# ============ Parking Area Endpoints ============

@app.get("/api/parking-areas", response_model=list[ParkingAreaResponse])
async def get_parking_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all parking areas"""
    parking_areas = db.query(ParkingArea).offset(skip).limit(limit).all()
    return parking_areas


@app.get("/api/parking-areas/{area_id}", response_model=ParkingAreaResponse)
async def get_parking_area(area_id: int, db: Session = Depends(get_db)):
    """Get specific parking area"""
    area = db.query(ParkingArea).filter(ParkingArea.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Parking area not found")
    return area


@app.post("/api/nearby-parkings", response_model=dict)
async def get_nearby_parkings(request: NearbyParkingRequest, db: Session = Depends(get_db)):
    """Get nearby parking areas with predictions"""
    # Fetch all parking areas from database
    areas = db.query(ParkingArea).all()
    
    # Convert to ParkingSpot objects with predictions
    parking_spots = []
    for area in areas:
        # Get availability data
        history = db.query(ParkingHistory).filter(
            ParkingHistory.parking_area_id == area.id
        ).order_by(ParkingHistory.timestamp.desc()).first()
        
        occupancy_rate = float(history.occupancy_rate) if history else 50.0
        traffic = history.traffic_density if history else "Medium"
        
        # Make prediction
        if model:
            pred_data = pd.DataFrame([{
                'time_of_day': datetime.utcnow().hour,
                'day_of_week': datetime.utcnow().weekday(),
                'location_id': area.id,
                'historical_occupancy_rate': occupancy_rate,
                'previous_duration_hours': 2.0,
                'traffic_density': traffic
            }])
            _, prob = model.predict(pred_data)
            availability_prob = float(prob[0])
        else:
            availability_prob = 1 - (occupancy_rate / 100)
        
        available_slots = db.query(ParkingSlot).filter(
            ParkingSlot.parking_area_id == area.id,
            ParkingSlot.is_available == True
        ).count()
        
        spot = ParkingSpot(
            id=area.id,
            name=area.name,
            latitude=float(area.latitude),
            longitude=float(area.longitude),
            available=available_slots > 0,
            availability_probability=availability_prob,
            distance_km=0.5,  # Calculate actual distance
            traffic_level=traffic,
            price_per_hour=float(area.price_per_hour),
            total_slots=area.total_slots,
            available_slots=available_slots
        )
        parking_spots.append(spot)
    
    # Rank recommendations
    recommendations = recommendation_engine.rank_spots(
        parking_spots,
        request.latitude,
        request.longitude
    )
    
    return {"recommendations": recommendations}


# ============ Booking Endpoints ============

@app.post("/api/bookings", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a parking booking"""
    # Verify slot exists and is available
    slot = db.query(ParkingSlot).filter(ParkingSlot.id == booking.parking_slot_id).first()
    if not slot or not slot.is_available:
        raise HTTPException(status_code=404, detail="Parking slot not available")
    
    # Create booking
    db_booking = Booking(
        user_id=user_id,
        parking_slot_id=booking.parking_slot_id,
        check_in_time=booking.check_in_time,
        status="active"
    )
    
    # Mark slot as unavailable
    slot.is_available = False
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@app.get("/api/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking details"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking


@app.post("/api/bookings/{booking_id}/checkout")
async def checkout_booking(
    booking_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check out from parking"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Calculate duration and amount
    checkout_time = datetime.utcnow()
    duration = (checkout_time - booking.check_in_time).total_seconds() / 3600
    
    slot = db.query(ParkingSlot).filter(ParkingSlot.id == booking.parking_slot_id).first()
    area = db.query(ParkingArea).filter(ParkingArea.id == slot.parking_area_id).first()
    
    amount = duration * float(area.price_per_hour)
    
    # Update booking
    booking.check_out_time = checkout_time
    booking.duration_hours = duration
    booking.amount_paid = amount
    booking.status = "completed"
    
    # Mark slot as available
    slot.is_available = True
    
    db.commit()
    db.refresh(booking)
    
    return {
        "booking_id": booking.id,
        "duration_hours": round(duration, 2),
        "amount_paid": round(amount, 2),
        "status": "completed"
    }


# ============ Health Check ============

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Smart Parking API",
        "version": "1.0.0",
        "ml_model_loaded": model is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
