"""
Complete ML Model Training Script
Trains and compares Logistic Regression, Random Forest, and XGBoost models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, confusion_matrix, 
                            classification_report, roc_curve, auc)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import os
from datetime import datetime

class ModelTrainer:
    """Train and evaluate multiple ML models for parking availability prediction"""
    
    def __init__(self, data_path: str, models_dir: str = 'models'):
        """
        Initialize trainer with data
        
        Args:
            data_path: Path to training data CSV
            models_dir: Directory to save trained models
        """
        self.data_path = data_path
        self.models_dir = models_dir
        self.data = None
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        
        os.makedirs(models_dir, exist_ok=True)
    
    def load_data(self):
        """Load training data from CSV"""
        print(f"Loading data from {self.data_path}...")
        self.data = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.data)} samples")
        print(f"Features: {self.data.columns.tolist()}")
        return self.data
    
    def split_data(self, test_size: float = 0.2, val_size: float = 0.1):
        """Split data into train, validation, and test sets"""
        # Prepare features and target
        X = self.data.drop('is_available', axis=1)
        y = self.data['is_available']
        
        # Encode categorical features
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
        
        # Initial train-test split
        X_temp, self.X_test, y_temp, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Further split temp into train and validation
        val_ratio = val_size / (1 - test_size)
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )
        
        # Scale features
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_val_scaled = self.scaler.transform(self.X_val)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"\nData split:")
        print(f"  Train: {len(self.X_train)} samples")
        print(f"  Validation: {len(self.X_val)} samples")
        print(f"  Test: {len(self.X_test)} samples")
    
    def train_logistic_regression(self):
        """Train Logistic Regression baseline model"""
        print("\n" + "="*50)
        print("Training Logistic Regression...")
        print("="*50)
        
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['logistic_regression'] = model
        self._evaluate_model('logistic_regression', model)
    
    def train_random_forest(self, hyperparameter_tuning: bool = False):
        """Train Random Forest model"""
        print("\n" + "="*50)
        print("Training Random Forest...")
        print("="*50)
        
        if hyperparameter_tuning:
            print("Performing hyperparameter tuning...")
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 15, 20],
                'min_samples_split': [2, 5, 10],
            }
            rf = RandomForestClassifier(random_state=42, n_jobs=-1)
            grid_search = GridSearchCV(rf, param_grid, cv=3, n_jobs=-1)
            grid_search.fit(self.X_train_scaled, self.y_train)
            model = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")
        else:
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            model.fit(self.X_train_scaled, self.y_train)
        
        self.models['random_forest'] = model
        self._evaluate_model('random_forest', model)
    
    def train_xgboost(self):
        """Train XGBoost model"""
        print("\n" + "="*50)
        print("Training Gradient Boosting (XGBoost)...")
        print("="*50)
        
        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_leaf=5,
            random_state=42
        )
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['xgboost'] = model
        self._evaluate_model('xgboost', model)
    
    def _evaluate_model(self, model_name: str, model):
        """Evaluate model on validation and test sets"""
        # Validation predictions
        y_val_pred = model.predict(self.X_val_scaled)
        y_val_pred_proba = model.predict_proba(self.X_val_scaled)[:, 1]
        
        # Test predictions
        y_test_pred = model.predict(self.X_test_scaled)
        y_test_pred_proba = model.predict_proba(self.X_test_scaled)[:, 1]
        
        # Calculate metrics
        metrics = {
            'model_name': model_name,
            'val_accuracy': accuracy_score(self.y_val, y_val_pred),
            'val_precision': precision_score(self.y_val, y_val_pred, zero_division=0),
            'val_recall': recall_score(self.y_val, y_val_pred, zero_division=0),
            'val_f1': f1_score(self.y_val, y_val_pred, zero_division=0),
            'val_auc': roc_auc_score(self.y_val, y_val_pred_proba),
            'test_accuracy': accuracy_score(self.y_test, y_test_pred),
            'test_precision': precision_score(self.y_test, y_test_pred, zero_division=0),
            'test_recall': recall_score(self.y_test, y_test_pred, zero_division=0),
            'test_f1': f1_score(self.y_test, y_test_pred, zero_division=0),
            'test_auc': roc_auc_score(self.y_test, y_test_pred_proba),
            'training_date': datetime.now().isoformat()
        }
        
        self.results[model_name] = metrics
        
        # Print results
        print(f"\nValidation Metrics:")
        print(f"  Accuracy:  {metrics['val_accuracy']:.4f}")
        print(f"  Precision: {metrics['val_precision']:.4f}")
        print(f"  Recall:    {metrics['val_recall']:.4f}")
        print(f"  F1-Score:  {metrics['val_f1']:.4f}")
        print(f"  AUC-ROC:   {metrics['val_auc']:.4f}")
        
        print(f"\nTest Metrics:")
        print(f"  Accuracy:  {metrics['test_accuracy']:.4f}")
        print(f"  Precision: {metrics['test_precision']:.4f}")
        print(f"  Recall:    {metrics['test_recall']:.4f}")
        print(f"  F1-Score:  {metrics['test_f1']:.4f}")
        print(f"  AUC-ROC:   {metrics['test_auc']:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_test_pred)
        print(f"\nConfusion Matrix:")
        print(cm)
    
    def save_models(self):
        """Save all trained models to disk"""
        for model_name, model in self.models.items():
            filepath = os.path.join(self.models_dir, f'{model_name}_model.pkl')
            joblib.dump({
                'model': model,
                'scaler': self.scaler,
                'metrics': self.results.get(model_name)
            }, filepath)
            print(f"Saved {model_name} to {filepath}")
        
        # Save results summary
        results_file = os.path.join(self.models_dir, 'training_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Saved results to {results_file}")
    
    def compare_models(self):
        """Compare all trained models"""
        print("\n" + "="*70)
        print("MODEL COMPARISON")
        print("="*70)
        
        comparison_df = pd.DataFrame(self.results).T
        comparison_df = comparison_df[[
            'test_accuracy', 'test_precision', 'test_recall', 'test_f1', 'test_auc'
        ]]
        comparison_df.columns = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']
        
        print("\n" + comparison_df.to_string())
        
        # Find best model
        best_model = comparison_df['F1-Score'].idxmax()
        print(f"\nBest Model: {best_model} (F1-Score: {comparison_df.loc[best_model, 'F1-Score']:.4f})")
        
        return comparison_df
    
    def get_feature_importance(self, model_name: str = 'random_forest'):
        """Get feature importance for tree-based models"""
        if model_name not in self.models:
            print(f"Model {model_name} not trained")
            return
        
        model = self.models[model_name]
        
        # Get feature names
        feature_names = self.data.drop('is_available', axis=1).columns.tolist()
        
        if model_name == 'logistic_regression':
            importances = np.abs(model.coef_[0])
        else:  # Tree-based models
            importances = model.feature_importances_
        
        # Create dataframe
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        print(f"\nFeature Importance ({model_name}):")
        print(importance_df.to_string(index=False))
        
        return importance_df


def main():
    """Main training pipeline"""
    # Check if training data exists
    if not os.path.exists('training_data.csv'):
        print("Training data not found. Generating synthetic data...")
        from generate_training_data import generate_training_data
        generate_training_data(n_samples=10000, output_file='training_data.csv')
    
    # Initialize trainer
    trainer = ModelTrainer('training_data.csv')
    
    # Load and prepare data
    trainer.load_data()
    trainer.split_data()
    
    # Train models
    trainer.train_logistic_regression()
    trainer.train_random_forest(hyperparameter_tuning=False)
    trainer.train_xgboost()
    
    # Compare models
    comparison = trainer.compare_models()
    
    # Get feature importance
    trainer.get_feature_importance('random_forest')
    
    # Save models
    trainer.save_models()
    
    print("\n" + "="*50)
    print("Training completed successfully!")
    print("="*50)


if __name__ == "__main__":
    main()
