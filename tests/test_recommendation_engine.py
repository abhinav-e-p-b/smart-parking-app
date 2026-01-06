"""
Tests for recommendation engine
"""

import pytest
from backend.recommendation_engine import RecommendationEngine, ParkingSpot


@pytest.fixture
def sample_parking_spots():
    """Create sample parking spots"""
    spots = [
        ParkingSpot(
            id=1, name="Garage A", latitude=40.7128, longitude=-74.0060,
            available=True, availability_probability=0.85,
            distance_km=0.5, traffic_level="Low",
            price_per_hour=5.50, total_slots=150, available_slots=45
        ),
        ParkingSpot(
            id=2, name="Lot B", latitude=40.7138, longitude=-74.0070,
            available=True, availability_probability=0.62,
            distance_km=0.8, traffic_level="Medium",
            price_per_hour=3.00, total_slots=80, available_slots=18
        ),
        ParkingSpot(
            id=3, name="Garage C", latitude=40.7148, longitude=-74.0050,
            available=True, availability_probability=0.45,
            distance_km=1.2, traffic_level="High",
            price_per_hour=4.00, total_slots=200, available_slots=35
        ),
    ]
    return spots


def test_engine_initialization():
    """Test recommendation engine initialization"""
    engine = RecommendationEngine(max_distance_km=5.0)
    assert engine.max_distance_km == 5.0
    assert 'availability' in engine.weights


def test_haversine_distance():
    """Test distance calculation"""
    engine = RecommendationEngine()
    
    # Same location
    dist = engine.haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
    assert abs(dist) < 0.01
    
    # Known distance (approx 1.2 km)
    dist = engine.haversine_distance(40.7128, -74.0060, 40.7228, -74.0060)
    assert 1.0 < dist < 1.4


def test_score_availability(sample_parking_spots):
    """Test availability scoring"""
    engine = RecommendationEngine()
    spot = sample_parking_spots[0]
    
    score = engine.score_availability(spot)
    assert 0 <= score <= 1
    assert score == spot.availability_probability


def test_score_distance(sample_parking_spots):
    """Test distance scoring"""
    engine = RecommendationEngine()
    spot = sample_parking_spots[0]
    
    score = engine.score_distance(spot, 0.5)
    assert 0 <= score <= 1


def test_score_traffic(sample_parking_spots):
    """Test traffic scoring"""
    engine = RecommendationEngine()
    
    low_score = engine.score_traffic(sample_parking_spots[0])
    high_score = engine.score_traffic(sample_parking_spots[2])
    
    assert low_score > high_score


def test_rank_spots(sample_parking_spots):
    """Test parking spot ranking"""
    engine = RecommendationEngine()
    user_lat, user_lon = 40.7128, -74.0060
    
    recommendations = engine.rank_spots(sample_parking_spots, user_lat, user_lon)
    
    assert len(recommendations) <= len(sample_parking_spots)
    assert all('scores' in rec for rec in recommendations)
    
    # Check that recommendations are sorted by score
    scores = [rec['scores']['final'] for rec in recommendations]
    assert scores == sorted(scores, reverse=True)


def test_weights_normalization(sample_parking_spots):
    """Test that scoring weights sum to 1"""
    engine = RecommendationEngine()
    total_weight = sum(engine.weights.values())
    assert abs(total_weight - 1.0) < 0.001
