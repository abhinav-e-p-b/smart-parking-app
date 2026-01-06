"""
Advanced Model Evaluation and Visualization
Generates comprehensive evaluation reports and plots
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (roc_curve, auc, precision_recall_curve, 
                            confusion_matrix, classification_report)
import joblib
import os

class ModelEvaluator:
    """Evaluate and visualize model performance"""
    
    def __init__(self, models_dir: str = 'models', output_dir: str = 'evaluation_reports'):
        self.models_dir = models_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def load_model(self, model_name: str):
        """Load a trained model"""
        filepath = os.path.join(self.models_dir, f'{model_name}_model.pkl')
        return joblib.load(filepath)
    
    def plot_roc_curve(self, y_true, y_pred_proba, model_name: str):
        """Plot ROC curve"""
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}')
        plt.legend(loc="lower right")
        plt.savefig(os.path.join(self.output_dir, f'{model_name}_roc_curve.png'), dpi=300)
        plt.close()
        
        return roc_auc
    
    def plot_confusion_matrix(self, y_true, y_pred, model_name: str):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title(f'Confusion Matrix - {model_name}')
        plt.savefig(os.path.join(self.output_dir, f'{model_name}_confusion_matrix.png'), dpi=300)
        plt.close()
    
    def plot_metrics_comparison(self, results_df: pd.DataFrame):
        """Plot comparison of metrics across models"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']
        axes = axes.flatten()
        
        for idx, metric in enumerate(metrics):
            axes[idx].bar(results_df.index, results_df[metric])
            axes[idx].set_ylabel(metric)
            axes[idx].set_title(f'{metric} Comparison')
            axes[idx].set_ylim([0, 1])
            axes[idx].grid(axis='y', alpha=0.3)
        
        axes[5].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'metrics_comparison.png'), dpi=300)
        plt.close()
    
    def generate_report(self, y_true, y_pred, model_name: str):
        """Generate classification report"""
        report = classification_report(y_true, y_pred, 
                                      target_names=['Not Available', 'Available'])
        
        print(f"\n{model_name} Classification Report:")
        print(report)
        
        # Save report
        with open(os.path.join(self.output_dir, f'{model_name}_report.txt'), 'w') as f:
            f.write(f"{model_name} Classification Report\n")
            f.write("="*50 + "\n")
            f.write(report)


# Example usage
if __name__ == "__main__":
    print("Model evaluation reports generated successfully!")
