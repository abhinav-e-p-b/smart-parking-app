"""
Parking Recommendation Engine
Ranks and scores parking spots based on multiple criteria
"""

from typing import List, Dict
from dataclasses import dataclass
import math

@dataclass
class ParkingSpot:
    """Parking spot with prediction and metadata"""
    id: int
    name: str
    latitude: float
    longitude: float
    available: bool
    availability_probability: float  # 0-1
    distance_km: float
    traffic_level: str  # 'Low', 'Medium', 'High'
    price_per_hour: float
    total_slots: int
    available_slots: int


class RecommendationEngine:
    """
    Weighted scoring system for ranking parking spots
    
    Scoring Formula:
    Score = (0.4 × Availability%) + (0.3 × Distance_Weight) + 
            (0.2 × Traffic_Weight) + (0.1 × Price_Weight)
    """
    
    def __init__(self, max_distance_km: float = 5.0):
        """
        Initialize recommendation engine
        
        Args:
            max_distance_km: Maximum distance to consider (km)
        """
        self.max_distance_km = max_distance_km
        self.weights = {
            'availability': 0.4,
            'distance': 0.3,
            'traffic': 0.2,
            'price': 0.1
        }
    
    def normalize_score(self, value: float, min_val: float = 0, 
                       max_val: float = 1, inverse: bool = False) -> float:
        """
        Normalize a score to 0-1 range
        
        Args:
            value: Value to normalize
            min_val: Minimum value in range
            max_val: Maximum value in range
            inverse: If True, higher value = lower score
        """
        normalized = (value - min_val) / (max_val - min_val + 1e-6)
        normalized = max(0, min(1, normalized))  # Clamp to [0, 1]
        return 1 - normalized if inverse else normalized
    
    def score_availability(self, spot: ParkingSpot) -> float:
        """Score based on availability probability (0-1)"""
        return spot.availability_probability
    
    def score_distance(self, spot: ParkingSpot, user_distance: float) -> float:
        """
        Score based on distance (closer = higher score)
        
        Args:
            spot: Parking spot
            user_distance: Distance from user to spot (km)
        """
        # Normalize distance: 0 km = 1.0, max_distance = 0.0
        return 1 - min(user_distance / self.max_distance_km, 1.0)
    
    def score_traffic(self, spot: ParkingSpot) -> float:
        """Score based on traffic conditions (low traffic = higher score)"""
        traffic_scores = {
            'Low': 1.0,
            'Medium': 0.6,
            'High': 0.2
        }
        return traffic_scores.get(spot.traffic_level, 0.5)
    
    def score_price(self, spot: ParkingSpot, spots: List[ParkingSpot]) -> float:
        """
        Score based on price (cheaper = higher score)
        
        Args:
            spot: Parking spot
            spots: All available spots (for normalization)
        """
        prices = [s.price_per_hour for s in spots if s.price_per_hour]
        if not prices:
            return 0.5
        
        min_price = min(prices)
        max_price = max(prices)
        return 1 - self.normalize_score(spot.price_per_hour, min_price, max_price)
    
    def rank_spots(self, spots: List[ParkingSpot], 
                   user_lat: float, user_lon: float) -> List[Dict]:
        """
        Rank parking spots and return recommendations
        
        Args:
            spots: List of parking spots
            user_lat: User's current latitude
            user_lon: User's current longitude
        
        Returns:
            List of spots with scores, ranked by recommendation score
        """
        recommendations = []
        
        for spot in spots:
            # Calculate distance using Haversine formula
            distance = self.haversine_distance(
                user_lat, user_lon, spot.latitude, spot.longitude
            )
            
            # Skip if too far
            if distance > self.max_distance_km:
                continue
            
            # Calculate component scores
            availability_score = self.score_availability(spot)
            distance_score = self.score_distance(spot, distance)
            traffic_score = self.score_traffic(spot)
            price_score = self.score_price(spot, spots)
            
            # Calculate weighted final score
            final_score = (
                self.weights['availability'] * availability_score +
                self.weights['distance'] * distance_score +
                self.weights['traffic'] * traffic_score +
                self.weights['price'] * price_score
            )
            
            recommendations.append({
                'spot_id': spot.id,
                'name': spot.name,
                'latitude': spot.latitude,
                'longitude': spot.longitude,
                'availability_probability': spot.availability_probability,
                'distance_km': round(distance, 2),
                'traffic_level': spot.traffic_level,
                'price_per_hour': spot.price_per_hour,
                'available_slots': spot.available_slots,
                'total_slots': spot.total_slots,
                'confidence': round(spot.availability_probability * 100, 1),
                'scores': {
                    'availability': round(availability_score, 3),
                    'distance': round(distance_score, 3),
                    'traffic': round(traffic_score, 3),
                    'price': round(price_score, 3),
                    'final': round(final_score, 3)
                }
            })
        
        # Sort by final score (descending)
        recommendations.sort(key=lambda x: x['scores']['final'], reverse=True)
        return recommendations
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1, lon1: User coordinates (degrees)
            lat2, lon2: Spot coordinates (degrees)
        
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
