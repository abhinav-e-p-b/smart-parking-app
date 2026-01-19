import easyocr
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
import re
from typing import Optional, Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NumberPlateOCR:
    """
    Number plate recognition service using EasyOCR
    Handles vehicle license plate detection and text extraction
    """
    
    def __init__(self):
        """Initialize the OCR reader for license plate detection"""
        # Initialize reader for English text detection
        self.reader = easyocr.Reader(['en'], gpu=False)
        logger.info("EasyOCR reader initialized")
    
    def extract_plate_text(self, image_path: str) -> Optional[str]:
        """
        Extract text from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted license plate text or None if not found
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Perform OCR
            results = self.reader.readtext(image)
            
            # Extract and process text
            plate_text = self._process_ocr_results(results)
            return plate_text
            
        except Exception as e:
            logger.error(f"Error extracting plate text: {str(e)}")
            return None
    
    def extract_plate_from_base64(self, image_base64: str) -> Optional[str]:
        """
        Extract text from a base64 encoded image
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Extracted license plate text or None if not found
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Perform OCR
            results = self.reader.readtext(image_array)
            
            # Extract and process text
            plate_text = self._process_ocr_results(results)
            return plate_text
            
        except Exception as e:
            logger.error(f"Error extracting plate from base64: {str(e)}")
            return None
    
    def extract_plate_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """
        Extract text from image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Extracted license plate text or None if not found
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image from bytes")
                return None
            
            # Perform OCR
            results = self.reader.readtext(image)
            
            # Extract and process text
            plate_text = self._process_ocr_results(results)
            return plate_text
            
        except Exception as e:
            logger.error(f"Error extracting plate from bytes: {str(e)}")
            return None
    
    def _process_ocr_results(self, results: List) -> Optional[str]:
        """
        Process OCR results and extract the most likely license plate text
        
        Args:
            results: List of OCR detection results from EasyOCR
            
        Returns:
            Cleaned license plate text or None if not found
        """
        if not results:
            return None
        
        # Combine all detected text with confidence scores
        texts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.3:  # Only consider detections with >30% confidence
                texts.append({
                    'text': text.upper().strip(),
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        if not texts:
            return None
        
        # Sort by confidence and take the best matches
        texts.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Combine top results
        combined_text = ' '.join([item['text'] for item in texts[:5]])
        
        # Clean up the text to extract license plate
        plate = self._clean_plate_text(combined_text)
        
        return plate if plate else None
    
    def _clean_plate_text(self, text: str) -> Optional[str]:
        """
        Clean and validate extracted text to match license plate format
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and validated license plate text
        """
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^A-Z0-9\s]', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Common license plate formats:
        # US: AAA1234, A1A1AA, etc.
        # UK: AB12ABC, A123ABC, etc.
        # India: DL01AB1234, etc.
        
        # Extract sequences that look like license plates
        # Pattern: 2-3 letters followed by numbers or mix
        patterns = [
            r'[A-Z]{1,3}\s?[0-9]{1,4}',  # Matches patterns like "AB 1234"
            r'[A-Z]{2,3}[0-9]{2,4}[A-Z]{0,3}',  # UK/EU format
            r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}',  # Indian format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cleaned)
            if match:
                return match.group(0).replace(' ', '')
        
        # If no pattern matches but we have alphanumeric, return cleaned version
        if len(cleaned) >= 4 and len(cleaned) <= 15:
            return cleaned.replace(' ', '')
        
        return None
    
    def get_plate_region(self, image_path: str, min_confidence: float = 0.3) -> Optional[Tuple]:
        """
        Get the bounding box of detected license plate
        
        Args:
            image_path: Path to the image
            min_confidence: Minimum confidence threshold
            
        Returns:
            Tuple of (text, bbox, confidence) or None
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            results = self.reader.readtext(image)
            
            # Find the most confident detection
            best_result = None
            for (bbox, text, confidence) in results:
                if confidence > min_confidence:
                    if best_result is None or confidence > best_result[2]:
                        best_result = (text.upper(), bbox, confidence)
            
            return best_result
            
        except Exception as e:
            logger.error(f"Error getting plate region: {str(e)}")
            return None


# Singleton instance
_ocr_instance = None

def get_ocr_service() -> NumberPlateOCR:
    """Get or create singleton OCR service instance"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = NumberPlateOCR()
    return _ocr_instance
