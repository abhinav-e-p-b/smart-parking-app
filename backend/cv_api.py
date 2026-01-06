"""
Computer Vision API endpoints for parking slot detection
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import shutil
import tempfile
from pathlib import Path
from computer_vision import ParkingSlotDetector
from database import get_db
from sqlalchemy.orm import Session
from models import ParkingArea, ParkingHistory
from datetime import datetime

app = FastAPI(title="CV Detection API", version="1.0.0")

# Initialize detector
detector = ParkingSlotDetector(model_type="opencv")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/cv/detect-slots")
async def detect_parking_slots(
    file: UploadFile = File(...),
    parking_area_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Detect parking slots in uploaded image
    
    Returns:
        Detection results with occupancy information
    """
    try:
        # Save uploaded file
        temp_file = f"{UPLOAD_DIR}/{file.filename}"
        with open(temp_file, "wb") as buffer:
            buffer.write(await file.read())
        
        # Run detection
        results = detector.detect_parking_slots(temp_file)
        
        # Update database if parking_area_id provided
        if parking_area_id and db:
            history = ParkingHistory(
                parking_area_id=parking_area_id,
                day_of_week=datetime.utcnow().weekday(),
                hour_of_day=datetime.utcnow().hour,
                occupancy_rate=results["occupancy_rate"],
                available_slots=results["available_slots"],
                total_slots=results["total_slots"],
                traffic_density="Medium",  # Default - could be enhanced
                timestamp=datetime.utcnow()
            )
            db.add(history)
            db.commit()
        
        # Clean up temp file
        os.remove(temp_file)
        
        return {
            "success": True,
            "detection_results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Detection error: {str(e)}")


@app.post("/api/cv/draw-detections")
async def draw_detections(
    file: UploadFile = File(...)
):
    """
    Draw detection results on image and return annotated image
    """
    try:
        # Save uploaded file
        temp_file = f"{UPLOAD_DIR}/{file.filename}"
        with open(temp_file, "wb") as buffer:
            buffer.write(await file.read())
        
        # Generate output filename
        output_file = f"{UPLOAD_DIR}/annotated_{file.filename}"
        
        # Draw results
        detector.draw_detection_results(temp_file, output_file)
        
        # Return annotated image
        return FileResponse(output_file, media_type="image/jpeg")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing error: {str(e)}")


@app.get("/api/cv/model-info")
async def get_model_info():
    """Get information about the CV model"""
    return {
        "model_type": detector.model_type,
        "confidence_threshold": detector.confidence_threshold,
        "nms_threshold": detector.nms_threshold,
        "description": "Parking slot detection using OpenCV and contour analysis"
    }
