#!/bin/bash

# Deploy using Docker Compose

echo "Building and starting containers..."

# Build images
docker-compose build

# Start services
docker-compose up -d

# Initialize database
echo "Initializing database..."
docker-compose exec postgres psql -U smart_parking_user -d smart_parking -f /docker-entrypoint-initdb.d/01-schema.sql

echo "Deployment complete!"
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  Database: localhost:5432"
