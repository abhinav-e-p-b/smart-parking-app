"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user creation"""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParkingAreaResponse(BaseModel):
    """Schema for parking area response"""
    id: int
    name: str
    latitude: float
    longitude: float
    total_slots: int
    address: Optional[str]
    price_per_hour: float


class ParkingSlotResponse(BaseModel):
    """Schema for parking slot response"""
    id: int
    slot_number: str
    is_available: bool
    vehicle_type: Optional[str]
    parking_area_id: int


class PredictionRequest(BaseModel):
    """Schema for prediction request"""
    time_of_day: int
    day_of_week: int
    location_id: int
    historical_occupancy_rate: float
    previous_duration_hours: float
    traffic_density: str


class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    location_id: int
    prediction: str
    availability_probability: float
    confidence: float
    timestamp: datetime


class NearbyParkingRequest(BaseModel):
    """Schema for nearby parking request"""
    latitude: float
    longitude: float
    radius_km: Optional[float] = 5.0


class RecommendationScores(BaseModel):
    """Scoring breakdown"""
    availability: float
    distance: float
    traffic: float
    price: float
    final: float


class ParkingRecommendation(BaseModel):
    """Schema for parking recommendation"""
    spot_id: int
    name: str
    latitude: float
    longitude: float
    availability_probability: float
    distance_km: float
    traffic_level: str
    price_per_hour: float
    available_slots: int
    total_slots: int
    confidence: float
    scores: RecommendationScores


class BookingCreate(BaseModel):
    """Schema for booking creation"""
    parking_slot_id: int
    check_in_time: datetime


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: int
    user_id: int
    parking_slot_id: int
    check_in_time: datetime
    check_out_time: Optional[datetime]
    status: str
    duration_hours: Optional[float]
    amount_paid: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True
