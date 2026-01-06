"""
Generate synthetic training data for Smart Parking ML model
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_training_data(n_samples=10000, output_file='training_data.csv'):
    """
    Generate synthetic parking history data
    
    Features:
    - time_of_day: 0-23
    - day_of_week: 0-6
    - location_id: 1-50
    - historical_occupancy_rate: 0-100
    - previous_duration_hours: 0.5-8
    - traffic_density: Low/Medium/High
    - is_available: 1/0 (target variable)
    """
    
    np.random.seed(42)
    
    data = {
        'time_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'location_id': np.random.randint(1, 51, n_samples),
        'historical_occupancy_rate': np.random.uniform(0, 100, n_samples),
        'previous_duration_hours': np.random.uniform(0.5, 8, n_samples),
        'traffic_density': np.random.choice(['Low', 'Medium', 'High'], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variable with realistic patterns
    # More likely available during night hours
    # Less likely during rush hours (7-9am, 5-7pm)
    # Inversely correlated with occupancy rate
    
    availability_probabilities = np.zeros(n_samples)
    
    for i in range(n_samples):
        base_prob = 0.6
        hour = df.loc[i, 'time_of_day']
        occupancy = df.loc[i, 'historical_occupancy_rate']
        traffic = df.loc[i, 'traffic_density']
        
        # Hour adjustment
        if 6 <= hour < 9 or 17 <= hour < 19:  # Rush hours
            base_prob -= 0.3
        elif 22 <= hour or hour < 6:  # Night time
            base_prob += 0.2
        
        # Occupancy adjustment
        base_prob -= (occupancy / 100) * 0.4
        
        # Traffic adjustment
        if traffic == 'High':
            base_prob -= 0.15
        elif traffic == 'Medium':
            base_prob -= 0.05
        
        availability_probabilities[i] = max(0.1, min(0.9, base_prob))
    
    # Generate binary target based on probabilities
    df['is_available'] = (np.random.random(n_samples) < availability_probabilities).astype(int)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"Generated {n_samples} training samples")
    print(f"Saved to {output_file}")
    print(f"\nDataset statistics:")
    print(f"- Availability rate: {df['is_available'].mean()*100:.1f}%")
    print(f"- Time range: {df['time_of_day'].min()}-{df['time_of_day'].max()} hours")
    print(f"- Location range: {df['location_id'].min()}-{df['location_id'].max()}")
    print(f"- Occupancy range: {df['historical_occupancy_rate'].min():.1f}-{df['historical_occupancy_rate'].max():.1f}%")
    
    return df


if __name__ == "__main__":
    generate_training_data(n_samples=10000, output_file='training_data.csv')
