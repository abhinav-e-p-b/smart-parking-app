#!/bin/bash

# Smart Parking Application Setup Script
# Sets up development environment

set -e

echo "Setting up Smart Parking Application..."

# Create virtual environment
echo "Creating Python virtual environment..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Generate training data
echo "Generating training data..."
python scripts/generate_training_data.py

# Train models
echo "Training ML models..."
python scripts/train_models.py

# Create models directory
mkdir -p models

echo ""
echo "Backend setup complete!"
echo ""

# Frontend setup
cd ../frontend
echo "Installing frontend dependencies..."
npm install

echo ""
echo "Setup complete! To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
