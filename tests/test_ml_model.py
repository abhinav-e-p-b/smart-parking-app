"""
Unit tests for ML model training and prediction
"""

import pytest
import pandas as pd
import numpy as np
from backend.ml_model import ParkingAvailabilityModel


@pytest.fixture
def sample_data():
    """Create sample training data"""
    np.random.seed(42)
    data = pd.DataFrame({
        'time_of_day': np.random.randint(0, 24, 1000),
        'day_of_week': np.random.randint(0, 7, 1000),
        'location_id': np.random.randint(1, 50, 1000),
        'historical_occupancy_rate': np.random.uniform(0, 100, 1000),
        'previous_duration_hours': np.random.uniform(0.5, 8, 1000),
        'traffic_density': np.random.choice(['Low', 'Medium', 'High'], 1000),
    })
    
    target = pd.Series(np.random.binomial(1, 0.6, 1000))
    return data, target


def test_model_initialization():
    """Test model initialization"""
    model = ParkingAvailabilityModel(model_type='random_forest')
    assert model.model_type == 'random_forest'
    assert model.model is not None


def test_feature_engineering(sample_data):
    """Test feature engineering"""
    data, _ = sample_data
    model = ParkingAvailabilityModel()
    X, features = model.engineer_features(data)
    
    assert X.shape[0] == len(data)
    assert len(features) > 0
    assert all(col in X.columns for col in features)


def test_model_training(sample_data):
    """Test model training"""
    data, target = sample_data
    model = ParkingAvailabilityModel(model_type='logistic_regression')
    metrics = model.train(data, target)
    
    assert 'test_accuracy' in metrics
    assert 0 <= metrics['test_accuracy'] <= 1
    assert 'test_f1' in metrics
    assert model.model is not None


def test_prediction(sample_data):
    """Test prediction"""
    data, target = sample_data
    model = ParkingAvailabilityModel(model_type='random_forest')
    model.train(data, target)
    
    # Prepare test data
    test_data = data.iloc[:10]
    predictions, probabilities = model.predict(test_data)
    
    assert len(predictions) == 10
    assert len(probabilities) == 10
    assert all(p >= 0 and p <= 1 for p in probabilities)


def test_model_save_load(sample_data, tmp_path):
    """Test model serialization"""
    data, target = sample_data
    model = ParkingAvailabilityModel(model_type='random_forest')
    model.train(data, target)
    
    # Save model
    model_path = tmp_path / "test_model.pkl"
    model.save(str(model_path))
    
    # Load model
    loaded_model = ParkingAvailabilityModel.load(str(model_path))
    
    assert loaded_model.model is not None
    assert loaded_model.feature_names == model.feature_names


def test_model_comparison(sample_data):
    """Test multiple models for comparison"""
    data, target = sample_data
    models_to_test = ['logistic_regression', 'random_forest']
    
    results = {}
    for model_type in models_to_test:
        model = ParkingAvailabilityModel(model_type=model_type)
        metrics = model.train(data, target)
        results[model_type] = metrics['test_f1']
    
    # Both models should have non-zero F1 scores
    assert all(score > 0 for score in results.values())
