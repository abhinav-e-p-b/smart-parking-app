"""
Smart Parking ML Model Training & Inference
Implements Logistic Regression, Random Forest, and XGBoost models
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import json
from datetime import datetime
from typing import Dict, Tuple, List

class ParkingAvailabilityModel:
    """
    Machine Learning model for predicting parking availability.
    Supports multiple model types: Logistic Regression, Random Forest, XGBoost
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize the model
        
        Args:
            model_type: 'logistic_regression', 'random_forest', or 'xgboost'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.model_metadata = {}
        
        if model_type == "logistic_regression":
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "xgboost":
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def engineer_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Feature engineering: prepare features for model
        
        Args:
            data: Raw dataframe with columns:
                  - time_of_day (0-23)
                  - day_of_week (0-6)
                  - location_id
                  - historical_occupancy_rate
                  - previous_duration_hours
                  - traffic_density
        
        Returns:
            Engineered features dataframe and feature names
        """
        df = data.copy()
        features = []
        
        # Time-based features
        df['hour'] = df['time_of_day'].astype(int)
        df['is_morning_rush'] = ((df['hour'] >= 6) & (df['hour'] < 9)).astype(int)
        df['is_evening_rush'] = ((df['hour'] >= 17) & (df['hour'] < 19)).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)
        
        features.extend(['hour', 'is_morning_rush', 'is_evening_rush', 'is_night'])
        
        # Day-based features
        df['day_of_week'] = df['day_of_week'].astype(int)
        df['is_weekend'] = ((df['day_of_week'] >= 5)).astype(int)
        
        features.extend(['day_of_week', 'is_weekend'])
        
        # Occupancy and duration features
        df['historical_occupancy_rate'] = df['historical_occupancy_rate'].fillna(50)
        df['occupancy_normalized'] = df['historical_occupancy_rate'] / 100
        df['previous_duration_hours'] = df['previous_duration_hours'].fillna(2)
        
        features.extend(['occupancy_normalized', 'previous_duration_hours'])
        
        # Traffic density encoding
        if 'traffic_density' in df.columns:
            traffic_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
            df['traffic_encoded'] = df['traffic_density'].map(traffic_mapping).fillna(1)
            features.append('traffic_encoded')
        
        # Location encoding (if applicable)
        if 'location_id' in df.columns:
            df['location_encoded'] = df['location_id']
            features.append('location_encoded')
        
        self.feature_names = features
        return df[features], features
    
    def train(self, data: pd.DataFrame, target: pd.Series, 
              test_size: float = 0.2, val_size: float = 0.1) -> Dict:
        """
        Train the model and evaluate performance
        
        Args:
            data: Training data (raw features)
            target: Target variable (is_available: 0/1)
            test_size: Proportion of test data
            val_size: Proportion of validation data
        
        Returns:
            Dictionary with training metrics
        """
        # Feature engineering
        X, features = self.engineer_features(data)
        y = target.values
        
        # Split data: train, validation, test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print(f"Training {self.model_type} model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate on validation set
        y_val_pred = self.model.predict(X_val_scaled)
        y_val_pred_proba = self.model.predict_proba(X_val_scaled)[:, 1]
        
        # Evaluate on test set
        y_test_pred = self.model.predict(X_test_scaled)
        y_test_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = {
            'model_type': self.model_type,
            'train_size': len(X_train),
            'val_size': len(X_val),
            'test_size': len(X_test),
            'val_accuracy': accuracy_score(y_val, y_val_pred),
            'val_precision': precision_score(y_val, y_val_pred, zero_division=0),
            'val_recall': recall_score(y_val, y_val_pred, zero_division=0),
            'val_f1': f1_score(y_val, y_val_pred, zero_division=0),
            'val_auc': roc_auc_score(y_val, y_val_pred_proba),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'test_precision': precision_score(y_test, y_test_pred, zero_division=0),
            'test_recall': recall_score(y_test, y_test_pred, zero_division=0),
            'test_f1': f1_score(y_test, y_test_pred, zero_division=0),
            'test_auc': roc_auc_score(y_test, y_test_pred_proba),
            'training_date': datetime.now().isoformat()
        }
        
        self.model_metadata = metrics
        
        print(f"\nModel Performance Metrics:")
        print(f"Validation - Accuracy: {metrics['val_accuracy']:.4f}, "
              f"Precision: {metrics['val_precision']:.4f}, "
              f"Recall: {metrics['val_recall']:.4f}, "
              f"F1: {metrics['val_f1']:.4f}, "
              f"AUC: {metrics['val_auc']:.4f}")
        print(f"Test - Accuracy: {metrics['test_accuracy']:.4f}, "
              f"Precision: {metrics['test_precision']:.4f}, "
              f"Recall: {metrics['test_recall']:.4f}, "
              f"F1: {metrics['test_f1']:.4f}, "
              f"AUC: {metrics['test_auc']:.4f}")
        
        return metrics
    
    def predict(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data
        
        Args:
            data: Raw feature data
        
        Returns:
            Predictions (0/1) and probabilities (0-1)
        """
        X, _ = self.engineer_features(data)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        return predictions, probabilities
    
    def feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if self.model_type == 'logistic_regression':
            importances = np.abs(self.model.coef_[0])
        else:  # Random Forest, XGBoost
            importances = self.model.feature_importances_
        
        return dict(zip(self.feature_names, importances))
    
    def save(self, filepath: str):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metadata': self.model_metadata
        }, filepath)
        print(f"Model saved to {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """Load model from disk"""
        data = joblib.load(filepath)
        instance = ParkingAvailabilityModel()
        instance.model = data['model']
        instance.scaler = data['scaler']
        instance.feature_names = data['feature_names']
        instance.model_metadata = data['metadata']
        return instance


# Example training script
if __name__ == "__main__":
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 10000
    
    train_data = pd.DataFrame({
        'time_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'location_id': np.random.randint(1, 50, n_samples),
        'historical_occupancy_rate': np.random.uniform(0, 100, n_samples),
        'previous_duration_hours': np.random.uniform(0.5, 8, n_samples),
        'traffic_density': np.random.choice(['Low', 'Medium', 'High'], n_samples)
    })
    
    # Target: availability (1 = available, 0 = occupied)
    # More likely available during night, less likely during rush hours
    target = pd.Series(
        np.random.binomial(1, p=0.6 - 0.2 * train_data['historical_occupancy_rate'] / 100)
    )
    
    # Train models
    models = {}
    for model_type in ['logistic_regression', 'random_forest']:
        model = ParkingAvailabilityModel(model_type=model_type)
        metrics = model.train(train_data, target)
        models[model_type] = model
        model.save(f'models/{model_type}_model.pkl')
    
    print("\nTraining completed successfully!")
