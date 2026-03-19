"""
Configuration settings for the Cyberbullying Detection System
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Data paths
TWITTER_DATA_PATH = os.path.join(DATA_DIR, 'twitter_hate_speech.csv')
WIKIPEDIA_DATA_PATH = os.path.join(DATA_DIR, 'wikipedia_attacks.csv')

# Model paths
TWITTER_MODEL_PATH = os.path.join(MODELS_DIR, 'twitter_svm_model.pkl')
TWITTER_VECTORIZER_PATH = os.path.join(MODELS_DIR, 'twitter_vectorizer.pkl')
WIKIPEDIA_MODEL_PATH = os.path.join(MODELS_DIR, 'wikipedia_rf_model.pkl')
WIKIPEDIA_VECTORIZER_PATH = os.path.join(MODELS_DIR, 'wikipedia_vectorizer.pkl')

# Preprocessing settings
RANDOM_SEED = 42
TEST_SIZE = 0.2
VAL_SIZE = 0.1

# TF-IDF settings (optimized for 4GB RAM)
MAX_FEATURES = 5000  # Limit vocabulary size
MIN_DF = 2
MAX_DF = 0.95
NGRAM_RANGE = (1, 2)

# Model hyperparameters
TWITTER_SVM_PARAMS = {
    'C': [0.1, 1, 10],
    'kernel': ['linear', 'rbf'],
    'gamma': ['scale', 'auto']
}

WIKIPEDIA_RF_PARAMS = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5]
}

# API settings
API_HOST = '0.0.0.0'
API_PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
