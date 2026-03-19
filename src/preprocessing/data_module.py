"""
DataModule: Handles data loading, splitting, and management
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import logging
import os


class DataModule:
    """
    Manages data loading, splitting, and preparation for model training.
    Ensures reproducibility with fixed random seed.
    """
    
    def __init__(self, random_seed=42, test_size=0.2, val_size=0.1):
        """
        Initialize DataModule with split parameters.
        
        Args:
            random_seed: Random seed for reproducibility
            test_size: Proportion of data for test set
            val_size: Proportion of training data for validation set
        """
        self.random_seed = random_seed
        self.test_size = test_size
        self.val_size = val_size
        
        self.logger = logging.getLogger(__name__)
        
        # Data containers
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        
    def load_twitter_data(self, filepath):
        """
        Load Twitter hate speech dataset.
        Expected columns: id, label, tweet
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with loaded data
        """
        self.logger.info(f"Loading Twitter data from {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Twitter data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        
        # Validate columns
        required_cols = ['tweet', 'label']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Twitter data must contain columns: {required_cols}")
        
        # Remove missing values
        df = df.dropna(subset=['tweet', 'label'])
        
        self.logger.info(f"Loaded {len(df)} Twitter samples")
        self.logger.info(f"Label distribution:\n{df['label'].value_counts()}")
        
        return df
    
    def load_wikipedia_data(self, filepath):
        """
        Load Wikipedia personal attacks dataset.
        Expected columns: review_id, comment, year, attack
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with loaded data
        """
        self.logger.info(f"Loading Wikipedia data from {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Wikipedia data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        
        # Validate columns
        required_cols = ['comment', 'attack']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Wikipedia data must contain columns: {required_cols}")
        
        # Remove missing values
        df = df.dropna(subset=['comment', 'attack'])
        
        self.logger.info(f"Loaded {len(df)} Wikipedia samples")
        self.logger.info(f"Label distribution:\n{df['attack'].value_counts()}")
        
        return df
    
    def prepare_data(self, texts, labels):
        """
        Prepare data by converting to numpy arrays and handling types.
        
        Args:
            texts: Text data (Series or list)
            labels: Label data (Series or list)
            
        Returns:
            Tuple of (texts_array, labels_array)
        """
        if isinstance(texts, pd.Series):
            texts = texts.values
        if isinstance(labels, pd.Series):
            labels = labels.values
            
        return np.array(texts), np.array(labels)
    
    def split_data(self, X, y, include_val=True):
        """
        Split data into train, validation, and test sets.
        
        Args:
            X: Feature data
            y: Labels
            include_val: Whether to create a validation set
            
        Returns:
            Dictionary with split data
        """
        self.logger.info(f"Splitting data with test_size={self.test_size}, val_size={self.val_size}")
        
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, 
            test_size=self.test_size, 
            random_state=self.random_seed,
            stratify=y
        )
        
        if include_val and self.val_size > 0:
            # Second split: train vs val
            val_size_adjusted = self.val_size / (1 - self.test_size)
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp,
                test_size=val_size_adjusted,
                random_state=self.random_seed,
                stratify=y_temp
            )
            
            self.X_train, self.X_val, self.X_test = X_train, X_val, X_test
            self.y_train, self.y_val, self.y_test = y_train, y_val, y_test
            
            self.logger.info(f"Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")
            
            return {
                'X_train': X_train,
                'X_val': X_val,
                'X_test': X_test,
                'y_train': y_train,
                'y_val': y_val,
                'y_test': y_test
            }
        else:
            self.X_train, self.X_test = X_temp, X_test
            self.y_train, self.y_test = y_temp, y_test
            
            self.logger.info(f"Train size: {len(X_temp)}, Test size: {len(X_test)}")
            
            return {
                'X_train': X_temp,
                'X_test': X_test,
                'y_train': y_temp,
                'y_test': y_test
            }
    
    def get_train_data(self):
        """Get training data."""
        return self.X_train, self.y_train
    
    def get_val_data(self):
        """Get validation data."""
        return self.X_val, self.y_val
    
    def get_test_data(self):
        """Get test data."""
        return self.X_test, self.y_test
    
    def get_data_stats(self):
        """
        Get statistics about the loaded data.
        
        Returns:
            Dictionary with data statistics
        """
        stats = {}
        
        if self.X_train is not None:
            stats['train_size'] = len(self.X_train)
            stats['train_label_dist'] = pd.Series(self.y_train).value_counts().to_dict()
        
        if self.X_val is not None:
            stats['val_size'] = len(self.X_val)
            stats['val_label_dist'] = pd.Series(self.y_val).value_counts().to_dict()
        
        if self.X_test is not None:
            stats['test_size'] = len(self.X_test)
            stats['test_label_dist'] = pd.Series(self.y_test).value_counts().to_dict()
        
        return stats
