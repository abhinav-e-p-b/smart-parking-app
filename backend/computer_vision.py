"""
Computer Vision Module for Parking Slot Detection
Uses YOLO/OpenCV for real-time parking space detection from images
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import os


class ParkingSlotDetector:
    """Detect free/occupied parking slots in images using computer vision"""
    
    def __init__(self, model_type: str = "yolo"):
        """
        Initialize detector
        
        Args:
            model_type: 'yolo', 'mobilenet', or 'opencv'
        """
        self.model_type = model_type
        self.model = None
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        
        if model_type == "yolo":
            self._init_yolo()
    
    def _init_yolo(self):
        """Initialize YOLO model"""
        try:
            # Try to load YOLOv5 or YOLOv8 (requires torch and ultralytics)
            # For production, use: ultralytics or yolov5
            print("YOLO model initialized (placeholder for actual implementation)")
        except ImportError:
            print("YOLOv5/v8 not installed. Using fallback CV method.")
            self.model_type = "opencv"
    
    def detect_parking_slots(self, image_path: str) -> Dict:
        """
        Detect parking slots in image
        
        Args:
            image_path: Path to parking lot image
        
        Returns:
            Dictionary with detection results
        """
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Image not found"}
        
        height, width = image.shape[:2]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect white lines (parking slot boundaries)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Find contours
        contours, _ = cv2.findContours(white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        parking_slots = []
        occupied_slots = []
        
        for contour in contours:
            # Filter contours by area (parking slots have specific dimensions)
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Typical parking slot size
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if slot is occupied by analyzing the interior
                roi = image[y:y+h, x:x+w]
                occupancy_score = self._calculate_occupancy(roi)
                
                slot_info = {
                    "id": len(parking_slots),
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "occupancy_score": occupancy_score,
                    "is_occupied": occupancy_score > 0.5,
                    "confidence": min(occupancy_score, 1.0)
                }
                
                parking_slots.append(slot_info)
                
                if occupancy_score > 0.5:
                    occupied_slots.append(slot_info)
        
        # Calculate statistics
        total_slots = len(parking_slots)
        occupied_count = len(occupied_slots)
        available_count = total_slots - occupied_count
        occupancy_rate = (occupied_count / total_slots * 100) if total_slots > 0 else 0
        
        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_count,
            "available_slots": available_count,
            "occupancy_rate": round(occupancy_rate, 2),
            "slots": parking_slots,
            "image_dimensions": {"width": width, "height": height}
        }
    
    def _calculate_occupancy(self, roi: np.ndarray) -> float:
        """
        Calculate occupancy score for a parking slot
        
        Args:
            roi: Region of interest (parking slot image)
        
        Returns:
            Occupancy score (0-1), where 1 is occupied
        """
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Calculate edge density (more edges = likely occupied)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Calculate fill ratio
        fill_ratio = np.sum(closed > 0) / closed.size
        
        # Combined occupancy score
        occupancy_score = (edge_ratio * 0.4 + fill_ratio * 0.6)
        
        return min(occupancy_score, 1.0)
    
    def draw_detection_results(self, image_path: str, output_path: str):
        """
        Draw detection results on image
        
        Args:
            image_path: Input image path
            output_path: Output image with annotations
        """
        results = self.detect_parking_slots(image_path)
        image = cv2.imread(image_path)
        
        # Draw detected slots
        for slot in results.get("slots", []):
            x, y, w, h = slot["x"], slot["y"], slot["width"], slot["height"]
            
            # Color based on occupancy
            color = (0, 0, 255) if slot["is_occupied"] else (0, 255, 0)  # Red for occupied, green for free
            
            # Draw rectangle
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            # Add text
            text = f"{'Occupied' if slot['is_occupied'] else 'Free'}"
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Save result
        cv2.imwrite(output_path, image)
        print(f"Annotated image saved to {output_path}")
    
    def process_batch(self, image_dir: str) -> List[Dict]:
        """
        Process multiple parking lot images
        
        Args:
            image_dir: Directory containing parking lot images
        
        Returns:
            List of detection results
        """
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        for image_file in Path(image_dir).iterdir():
            if image_file.suffix.lower() in image_extensions:
                result = self.detect_parking_slots(str(image_file))
                result["image_name"] = image_file.name
                results.append(result)
        
        return results


# Example usage and testing
if __name__ == "__main__":
    print("Computer Vision Module for Parking Detection")
    print("=" * 50)
    
    # Initialize detector
    detector = ParkingSlotDetector(model_type="opencv")
    
    # Example: Process a sample image (would be provided by user)
    print("\nExample: Detecting parking slots in image...")
    print("To use this module:")
    print("1. Place parking lot images in a directory")
    print("2. Call detector.detect_parking_slots('path/to/image.jpg')")
    print("3. Results include occupancy rate and individual slot status")
