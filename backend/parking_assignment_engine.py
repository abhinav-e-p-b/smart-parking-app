import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParkingLot:
    lot_id: int
    name: str
    latitude: float
    longitude: float
    available_slots: int
    total_slots: int
    price_per_hour: float
    traffic_level: str
    rating: float

@dataclass
class VehicleInfo:
    plate_number: str
    latitude: float
    longitude: float
    vehicle_type: str = "car"

@dataclass
class AssignmentResult:
    lot_id: int
    lot_name: str
    assigned_slot: str
    distance_km: float
    estimated_cost: float
    duration_minutes: int
    confidence_score: float
    token_number: str

class ParkingAssignmentEngine:
    """
    AI-based parking lot assignment engine
    Assigns vehicles to optimal parking lots based on distance, availability, price, and ML predictions
    """
    
    def __init__(self, ml_model=None):
        """
        Initialize the assignment engine
        
        Args:
            ml_model: Optional ML model for prediction (Logistic Regression, Random Forest, XGBoost)
        """
        self.ml_model = ml_model
        self.parking_lots: Dict[int, ParkingLot] = {}
        self.assignments: Dict[str, AssignmentResult] = {}  # plate_number -> assignment
    
    def register_parking_lot(self, lot: ParkingLot) -> None:
        """Register a parking lot"""
        self.parking_lots[lot.lot_id] = lot
        logger.info(f"Registered parking lot: {lot.name} (ID: {lot.lot_id})")
    
    def update_lot_availability(self, lot_id: int, available_slots: int, total_slots: int) -> None:
        """Update parking lot availability"""
        if lot_id in self.parking_lots:
            self.parking_lots[lot_id].available_slots = available_slots
            self.parking_lots[lot_id].total_slots = total_slots
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def score_lot(self, lot: ParkingLot, vehicle: VehicleInfo) -> float:
        """
        Calculate composite score for a parking lot
        Score factors: availability (40%), distance (30%), traffic (20%), price (10%)
        
        Returns score between 0 and 1
        """
        # Availability score (0-1)
        availability_score = lot.available_slots / lot.total_slots if lot.total_slots > 0 else 0
        
        # Distance score (0-1) - closer is better
        distance = self.calculate_distance(vehicle.latitude, vehicle.longitude, lot.latitude, lot.longitude)
        distance_score = max(0, 1 - (distance / 5))  # Normalize to 5km max
        
        # Traffic score (0-1)
        traffic_scores = {
            "Very Low": 1.0,
            "Low": 0.9,
            "Medium": 0.6,
            "High": 0.3,
            "Very High": 0.1
        }
        traffic_score = traffic_scores.get(lot.traffic_level, 0.5)
        
        # Price score (0-1) - lower is better (normalized to $10/hour)
        price_score = max(0, 1 - (lot.price_per_hour / 10))
        
        # Composite score with weights
        composite_score = (
            availability_score * 0.40 +
            distance_score * 0.30 +
            traffic_score * 0.20 +
            price_score * 0.10
        )
        
        return composite_score
    
    def get_top_candidates(self, vehicle: VehicleInfo, top_n: int = 3) -> List[Tuple[ParkingLot, float]]:
        """
        Get top N candidate parking lots for a vehicle
        
        Args:
            vehicle: Vehicle information with location
            top_n: Number of top candidates to return
            
        Returns:
            List of (ParkingLot, score) tuples sorted by score descending
        """
        candidates = []
        
        for lot in self.parking_lots.values():
            # Skip if lot is full
            if lot.available_slots <= 0:
                continue
            
            # Calculate score
            score = self.score_lot(lot, vehicle)
            candidates.append((lot, score))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates[:top_n]
    
    def assign_parking(
        self,
        plate_number: str,
        vehicle: VehicleInfo,
        duration_minutes: int = 120,
        use_ml_confidence: bool = True
    ) -> Optional[AssignmentResult]:
        """
        Assign a vehicle to the optimal parking lot
        
        Args:
            plate_number: Vehicle license plate
            vehicle: Vehicle location and info
            duration_minutes: Expected parking duration
            use_ml_confidence: Whether to use ML model for confidence scoring
            
        Returns:
            AssignmentResult with lot assignment details
        """
        # Get top candidates
        candidates = self.get_top_candidates(vehicle)
        
        if not candidates:
            logger.warning(f"No available parking lots for vehicle {plate_number}")
            return None
        
        # Select top candidate
        best_lot, base_score = candidates[0]
        
        # Calculate features for ML model if available
        confidence_score = base_score
        if use_ml_confidence and self.ml_model:
            try:
                # Prepare features for ML model
                features = self._prepare_ml_features(best_lot, vehicle, duration_minutes)
                confidence_score = self.ml_model.predict_proba([features])[0][1]  # Probability of success
            except Exception as e:
                logger.warning(f"ML prediction failed, using base score: {e}")
                confidence_score = base_score
        
        # Generate token
        token_number = self._generate_token(plate_number, best_lot.lot_id)
        
        # Generate slot assignment
        assigned_slot = self._assign_slot(best_lot, plate_number)
        
        # Calculate cost
        estimated_cost = best_lot.price_per_hour * (duration_minutes / 60)
        
        # Calculate distance
        distance_km = self.calculate_distance(
            vehicle.latitude, vehicle.longitude,
            best_lot.latitude, best_lot.longitude
        )
        
        # Create assignment result
        assignment = AssignmentResult(
            lot_id=best_lot.lot_id,
            lot_name=best_lot.name,
            assigned_slot=assigned_slot,
            distance_km=round(distance_km, 2),
            estimated_cost=round(estimated_cost, 2),
            duration_minutes=duration_minutes,
            confidence_score=round(confidence_score * 100, 1),
            token_number=token_number
        )
        
        # Store assignment
        self.assignments[plate_number] = assignment
        
        # Decrease available slots
        best_lot.available_slots -= 1
        
        logger.info(f"Assigned {plate_number} to {best_lot.name}, Slot: {assigned_slot}, Token: {token_number}")
        
        return assignment
    
    def _prepare_ml_features(self, lot: ParkingLot, vehicle: VehicleInfo, duration: int) -> List[float]:
        """Prepare features for ML model prediction"""
        distance = self.calculate_distance(vehicle.latitude, vehicle.longitude, lot.latitude, lot.longitude)
        occupancy_rate = (lot.total_slots - lot.available_slots) / lot.total_slots if lot.total_slots > 0 else 0
        
        traffic_map = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}
        traffic_value = traffic_map.get(lot.traffic_level, 3)
        
        features = [
            distance,
            occupancy_rate,
            lot.price_per_hour,
            traffic_value,
            lot.rating,
            duration
        ]
        
        return features
    
    def _generate_token(self, plate_number: str, lot_id: int) -> str:
        """Generate a unique parking token"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        plate_short = plate_number[-4:].upper()
        token = f"PKG{lot_id}{plate_short}{timestamp}"
        return token
    
    def _assign_slot(self, lot: ParkingLot, plate_number: str) -> str:
        """Assign a specific parking slot"""
        # Simple slot assignment based on available slots count
        slot_number = lot.total_slots - lot.available_slots + 1
        slot_letter = chr(65 + ((slot_number - 1) // 10) % 26)  # A-Z
        slot_id = ((slot_number - 1) % 10) + 1
        return f"{lot.lot_id}-{slot_letter}{slot_id}"
    
    def release_parking(self, plate_number: str) -> bool:
        """Release a parking assignment"""
        if plate_number not in self.assignments:
            logger.warning(f"No assignment found for {plate_number}")
            return False
        
        assignment = self.assignments[plate_number]
        lot = self.parking_lots.get(assignment.lot_id)
        
        if lot:
            lot.available_slots += 1
            logger.info(f"Released parking for {plate_number} from lot {assignment.lot_name}")
        
        del self.assignments[plate_number]
        return True
    
    def get_assignment(self, plate_number: str) -> Optional[AssignmentResult]:
        """Get current assignment for a vehicle"""
        return self.assignments.get(plate_number)
    
    def get_lot_status(self, lot_id: int) -> Optional[Dict]:
        """Get current status of a parking lot"""
        lot = self.parking_lots.get(lot_id)
        if not lot:
            return None
        
        return {
            "lot_id": lot.lot_id,
            "name": lot.name,
            "available_slots": lot.available_slots,
            "total_slots": lot.total_slots,
            "occupancy_rate": round((lot.total_slots - lot.available_slots) / lot.total_slots * 100, 1),
            "price_per_hour": lot.price_per_hour,
            "traffic_level": lot.traffic_level,
            "rating": lot.rating
        }
    
    def get_all_assignments(self) -> Dict[str, AssignmentResult]:
        """Get all current assignments"""
        return self.assignments.copy()


# Singleton instance
_assignment_engine = None

def get_assignment_engine(ml_model=None) -> ParkingAssignmentEngine:
    """Get or create singleton assignment engine"""
    global _assignment_engine
    if _assignment_engine is None:
        _assignment_engine = ParkingAssignmentEngine(ml_model)
    return _assignment_engine
