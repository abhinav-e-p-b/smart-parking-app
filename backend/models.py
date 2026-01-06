"""
SQLAlchemy ORM models for database tables
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")


class ParkingArea(Base):
    """Parking area model"""
    __tablename__ = "parking_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    total_slots = Column(Integer)
    address = Column(String(255))
    price_per_hour = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    slots = relationship("ParkingSlot", back_populates="parking_area", cascade="all, delete-orphan")
    history = relationship("ParkingHistory", back_populates="parking_area", cascade="all, delete-orphan")


class ParkingSlot(Base):
    """Individual parking slot model"""
    __tablename__ = "parking_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    parking_area_id = Column(Integer, ForeignKey("parking_areas.id"), index=True)
    slot_number = Column(String(50))
    is_available = Column(Boolean, default=True)
    vehicle_type = Column(String(50))  # Standard, Compact, EV, Handicap
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parking_area = relationship("ParkingArea", back_populates="slots")
    bookings = relationship("Booking", back_populates="parking_slot")


class Booking(Base):
    """Parking booking model"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    parking_slot_id = Column(Integer, ForeignKey("parking_slots.id"))
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")  # active, completed, cancelled
    duration_hours = Column(Numeric(5, 2), nullable=True)
    amount_paid = Column(Numeric(8, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    parking_slot = relationship("ParkingSlot", back_populates="bookings")


class ParkingHistory(Base):
    """Parking history for ML training"""
    __tablename__ = "parking_history"
    
    id = Column(Integer, primary_key=True, index=True)
    parking_area_id = Column(Integer, ForeignKey("parking_areas.id"), index=True)
    day_of_week = Column(Integer)  # 0-6
    hour_of_day = Column(Integer)  # 0-23
    occupancy_rate = Column(Numeric(5, 2))
    available_slots = Column(Integer)
    total_slots = Column(Integer)
    traffic_density = Column(String(50))  # Low, Medium, High
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parking_area = relationship("ParkingArea", back_populates="history")


class MLTrainingData(Base):
    """ML training data table"""
    __tablename__ = "ml_training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    parking_area_id = Column(Integer, ForeignKey("parking_areas.id"), index=True)
    time_of_day = Column(Integer)
    day_of_week = Column(Integer)
    historical_occupancy_rate = Column(Numeric(5, 2))
    previous_duration_hours = Column(Numeric(5, 2))
    traffic_density = Column(String(50))
    is_available = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
