-- Create tables for smart parking automation system

-- Vehicles table - stores registered vehicles
CREATE TABLE IF NOT EXISTS vehicles (
  id SERIAL PRIMARY KEY,
  license_plate VARCHAR(20) NOT NULL UNIQUE,
  phone_number VARCHAR(15) NOT NULL,
  owner_name VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  vehicle_model VARCHAR(100),
  vehicle_color VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parking lots table
CREATE TABLE IF NOT EXISTS parking_lots (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  address VARCHAR(255) NOT NULL,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  total_slots INT NOT NULL,
  available_slots INT NOT NULL,
  price_per_hour DECIMAL(5, 2),
  has_thermal_printer BOOLEAN DEFAULT FALSE,
  printer_ip_address VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parking assignments table - tracks active parking
CREATE TABLE IF NOT EXISTS parking_assignments (
  id SERIAL PRIMARY KEY,
  vehicle_id INT NOT NULL REFERENCES vehicles(id),
  parking_lot_id INT NOT NULL REFERENCES parking_lots(id),
  slot_number VARCHAR(10),
  entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  exit_time TIMESTAMP,
  token_number VARCHAR(50) NOT NULL UNIQUE,
  qr_code TEXT,
  status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
  assignment_confidence DECIMAL(3, 2), -- ML model confidence score
  cost_estimated DECIMAL(8, 2),
  cost_final DECIMAL(8, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SMS notifications tracking
CREATE TABLE IF NOT EXISTS sms_notifications (
  id SERIAL PRIMARY KEY,
  vehicle_id INT NOT NULL REFERENCES vehicles(id),
  parking_assignment_id INT REFERENCES parking_assignments(id),
  phone_number VARCHAR(15) NOT NULL,
  message_type VARCHAR(50), -- assignment, reminder, exit, receipt
  message_content TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
  twilio_sid VARCHAR(100),
  error_message TEXT,
  sent_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- License plate recognition logs
CREATE TABLE IF NOT EXISTS plate_recognition_logs (
  id SERIAL PRIMARY KEY,
  license_plate VARCHAR(20),
  confidence_score DECIMAL(3, 2),
  image_url TEXT,
  camera_location VARCHAR(100),
  recognized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  vehicle_found BOOLEAN,
  vehicle_id INT REFERENCES vehicles(id),
  processing_time_ms INT
);

-- Thermal printer jobs
CREATE TABLE IF NOT EXISTS printer_jobs (
  id SERIAL PRIMARY KEY,
  parking_assignment_id INT NOT NULL REFERENCES parking_assignments(id),
  parking_lot_id INT NOT NULL REFERENCES parking_lots(id),
  ticket_content TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'pending', -- pending, printing, completed, failed
  error_message TEXT,
  print_time TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX IF NOT EXISTS idx_vehicles_phone ON vehicles(phone_number);
CREATE INDEX IF NOT EXISTS idx_parking_assignments_vehicle ON parking_assignments(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_parking_assignments_lot ON parking_assignments(parking_lot_id);
CREATE INDEX IF NOT EXISTS idx_parking_assignments_status ON parking_assignments(status);
CREATE INDEX IF NOT EXISTS idx_sms_notifications_vehicle ON sms_notifications(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_sms_notifications_status ON sms_notifications(status);
CREATE INDEX IF NOT EXISTS idx_plate_logs_plate ON plate_recognition_logs(license_plate);
