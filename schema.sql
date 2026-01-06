-- Smart Parking Application Database Schema

-- Users Table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parking Areas Table
CREATE TABLE parking_areas (
  id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  total_slots INT NOT NULL,
  address VARCHAR(255),
  price_per_hour DECIMAL(5, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parking Slots Table
CREATE TABLE parking_slots (
  id SERIAL PRIMARY KEY,
  parking_area_id INT NOT NULL REFERENCES parking_areas(id) ON DELETE CASCADE,
  slot_number VARCHAR(50) NOT NULL,
  is_available BOOLEAN DEFAULT TRUE,
  vehicle_type VARCHAR(50), -- Standard, Compact, EV, Handicap
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings Table
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  parking_slot_id INT NOT NULL REFERENCES parking_slots(id),
  check_in_time TIMESTAMP NOT NULL,
  check_out_time TIMESTAMP,
  status VARCHAR(50) DEFAULT 'active', -- active, completed, cancelled
  duration_hours DECIMAL(5, 2),
  amount_paid DECIMAL(8, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parking History Table (for ML training)
CREATE TABLE parking_history (
  id SERIAL PRIMARY KEY,
  parking_area_id INT NOT NULL REFERENCES parking_areas(id),
  day_of_week INT, -- 0=Monday, 6=Sunday
  hour_of_day INT, -- 0-23
  occupancy_rate DECIMAL(5, 2), -- Percentage
  available_slots INT,
  total_slots INT,
  traffic_density VARCHAR(50), -- Low, Medium, High
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML Training Data Table
CREATE TABLE ml_training_data (
  id SERIAL PRIMARY KEY,
  parking_area_id INT NOT NULL REFERENCES parking_areas(id),
  time_of_day INT,
  day_of_week INT,
  historical_occupancy_rate DECIMAL(5, 2),
  previous_duration_hours DECIMAL(5, 2),
  traffic_density VARCHAR(50),
  is_available BOOLEAN, -- Target variable
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_parking_areas_location ON parking_areas(latitude, longitude);
CREATE INDEX idx_parking_slots_area ON parking_slots(parking_area_id);
CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_bookings_slot ON bookings(parking_slot_id);
CREATE INDEX idx_parking_history_area_time ON parking_history(parking_area_id, timestamp);
CREATE INDEX idx_ml_training_data_area ON ml_training_data(parking_area_id);
