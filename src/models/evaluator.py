"""
Model Evaluator: Comprehensive evaluation metrics and visualization
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import logging
import os


class ModelEvaluator:
    """
    Handles model evaluation with comprehensive metrics and visualizations.
    """
    
    def __init__(self, model_name='model'):
        """
        Initialize evaluator.
        
        Args:
            model_name: Name of the model for logging and saving plots
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.results = {}
        
    def evaluate(self, y_true, y_pred, y_pred_proba=None):
        """
        Compute all evaluation metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional, for ROC-AUC)
            
        Returns:
            Dictionary with all metrics
        """
        self.logger.info(f"Evaluating {self.model_name}...")
        
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='binary', zero_division=0)
        recall = recall_score(y_true, y_pred, average='binary', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='binary', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # ROC-AUC (if probabilities provided)
        roc_auc = None
        if y_pred_proba is not None:
            try:
                roc_auc = roc_auc_score(y_true, y_pred_proba)
            except Exception as e:
                self.logger.warning(f"Could not compute ROC-AUC: {e}")
        
        # Store results
        self.results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm,
            'roc_auc': roc_auc
        }
        
        # Log results
        self.logger.info(f"Accuracy: {accuracy:.4f}")
        self.logger.info(f"Precision: {precision:.4f}")
        self.logger.info(f"Recall: {recall:.4f}")
        self.logger.info(f"F1-Score: {f1:.4f}")
        if roc_auc:
            self.logger.info(f"ROC-AUC: {roc_auc:.4f}")
        
        return self.results
    
    def print_classification_report(self, y_true, y_pred, target_names=None):
        """
        Print detailed classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            target_names: Names for classes (e.g., ['Non-Hate', 'Hate'])
        """
        if target_names is None:
            target_names = ['Class 0', 'Class 1']
        
        report = classification_report(y_true, y_pred, target_names=target_names)
        self.logger.info(f"\nClassification Report for {self.model_name}:\n{report}")
        print(f"\nClassification Report for {self.model_name}:")
        print(report)
        
        return report
    
    def plot_confusion_matrix(self, y_true, y_pred, save_path=None, 
                             class_names=None, normalize=False):
        """
        Plot confusion matrix heatmap.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_path: Path to save the plot
            class_names: Names for classes
            normalize: Whether to normalize the confusion matrix
        """
        if class_names is None:
            class_names = ['Class 0', 'Class 1']
        
        cm = confusion_matrix(y_true, y_pred)
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            fmt = '.2f'
            title = f'Normalized Confusion Matrix - {self.model_name}'
        else:
            fmt = 'd'
            title = f'Confusion Matrix - {self.model_name}'
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt=fmt, cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names,
                   cbar_kws={'label': 'Count' if not normalize else 'Proportion'})
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Confusion matrix saved to {save_path}")
        
        plt.close()
        
        return cm
    
    def plot_roc_curve(self, y_true, y_pred_proba, save_path=None):
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            save_path: Path to save the plot
        """
        if y_pred_proba is None:
            self.logger.warning("Cannot plot ROC curve without predicted probabilities")
            return
        
        try:
            fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
            roc_auc = roc_auc_score(y_true, y_pred_proba)
            
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, color='darkorange', lw=2, 
                    label=f'ROC curve (AUC = {roc_auc:.4f})')
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
                    label='Random Classifier')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title(f'ROC Curve - {self.model_name}')
            plt.legend(loc="lower right")
            plt.grid(alpha=0.3)
            plt.tight_layout()
            
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"ROC curve saved to {save_path}")
            
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Error plotting ROC curve: {e}")
    
    def plot_metrics_comparison(self, metrics_dict, save_path=None):
        """
        Plot bar chart comparing multiple metrics.
        
        Args:
            metrics_dict: Dictionary with metric names and values
            save_path: Path to save the plot
        """
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        values = [metrics_dict.get(m, 0) for m in metrics]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(metrics, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        plt.ylim([0, 1.0])
        plt.ylabel('Score')
        plt.title(f'Performance Metrics - {self.model_name}')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Metrics comparison saved to {save_path}")
        
        plt.close()
    
    def generate_full_report(self, y_true, y_pred, y_pred_proba=None,
                           class_names=None, save_dir='logs'):
        """
        Generate complete evaluation report with all metrics and plots.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            class_names: Names for classes
            save_dir: Directory to save plots
            
        Returns:
            Dictionary with all results
        """
        self.logger.info("=" * 60)
        self.logger.info(f"FULL EVALUATION REPORT - {self.model_name}")
        self.logger.info("=" * 60)
        
        # Compute metrics
        results = self.evaluate(y_true, y_pred, y_pred_proba)
        
        # Print classification report
        self.print_classification_report(y_true, y_pred, class_names)
        
        # Generate plots
        cm_path = os.path.join(save_dir, f'{self.model_name}_confusion_matrix.png')
        self.plot_confusion_matrix(y_true, y_pred, cm_path, class_names)
        
        if y_pred_proba is not None:
            roc_path = os.path.join(save_dir, f'{self.model_name}_roc_curve.png')
            self.plot_roc_curve(y_true, y_pred_proba, roc_path)
        
        metrics_path = os.path.join(save_dir, f'{self.model_name}_metrics.png')
        self.plot_metrics_comparison(results, metrics_path)
        
        self.logger.info("=" * 60)
        self.logger.info("Evaluation complete!")
        self.logger.info("=" * 60)
        
        return results
    
    def get_results(self):
        """Get stored evaluation results."""
        return self.results
