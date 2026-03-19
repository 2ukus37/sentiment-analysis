"""
Example script demonstrating the preprocessing pipeline.
Run this after placing your datasets in the data/ folder.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing import DataPreprocessor, DataModule
from src.utils import setup_logger, save_model
from config.config import *

# Setup logging
logger = setup_logger('preprocess_example')


def preprocess_twitter_data():
    """
    Example: Preprocess Twitter hate speech dataset.
    """
    logger.info("=" * 50)
    logger.info("TWITTER DATA PREPROCESSING")
    logger.info("=" * 50)
    
    # Initialize components
    data_module = DataModule(
        random_seed=RANDOM_SEED,
        test_size=TEST_SIZE,
        val_size=VAL_SIZE
    )
    
    preprocessor = DataPreprocessor(
        use_count_vectorizer=False,
        max_features=MAX_FEATURES,
        min_df=MIN_DF,
        max_df=MAX_DF,
        ngram_range=NGRAM_RANGE
    )
    
    # Load data
    df = data_module.load_twitter_data(TWITTER_DATA_PATH)
    
    # Prepare data
    texts, labels = data_module.prepare_data(df['tweet'], df['label'])
    
    # Split data
    splits = data_module.split_data(texts, labels, include_val=True)
    
    # Preprocess texts
    logger.info("Preprocessing training texts...")
    X_train_clean = preprocessor.preprocess_corpus(splits['X_train'])
    
    logger.info("Preprocessing validation texts...")
    X_val_clean = preprocessor.preprocess_corpus(splits['X_val'])
    
    logger.info("Preprocessing test texts...")
    X_test_clean = preprocessor.preprocess_corpus(splits['X_test'])
    
    # Vectorize
    logger.info("Vectorizing texts...")
    X_train_vec = preprocessor.fit_transform(X_train_clean)
    X_val_vec = preprocessor.transform(X_val_clean)
    X_test_vec = preprocessor.transform(X_test_clean)
    
    logger.info(f"Training features shape: {X_train_vec.shape}")
    logger.info(f"Validation features shape: {X_val_vec.shape}")
    logger.info(f"Test features shape: {X_test_vec.shape}")
    
    # Save vectorizer
    save_model(preprocessor.vectorizer, TWITTER_VECTORIZER_PATH)
    
    # Print statistics
    stats = data_module.get_data_stats()
    logger.info(f"Data statistics: {stats}")
    
    return {
        'X_train': X_train_vec,
        'X_val': X_val_vec,
        'X_test': X_test_vec,
        'y_train': splits['y_train'],
        'y_val': splits['y_val'],
        'y_test': splits['y_test'],
        'preprocessor': preprocessor
    }


def preprocess_wikipedia_data():
    """
    Example: Preprocess Wikipedia personal attacks dataset.
    """
    logger.info("=" * 50)
    logger.info("WIKIPEDIA DATA PREPROCESSING")
    logger.info("=" * 50)
    
    # Initialize components
    data_module = DataModule(
        random_seed=RANDOM_SEED,
        test_size=TEST_SIZE,
        val_size=VAL_SIZE
    )
    
    preprocessor = DataPreprocessor(
        use_count_vectorizer=False,
        max_features=MAX_FEATURES,
        min_df=MIN_DF,
        max_df=MAX_DF,
        ngram_range=NGRAM_RANGE
    )
    
    # Load data
    df = data_module.load_wikipedia_data(WIKIPEDIA_DATA_PATH)
    
    # Prepare data
    texts, labels = data_module.prepare_data(df['comment'], df['attack'])
    
    # Split data
    splits = data_module.split_data(texts, labels, include_val=True)
    
    # Preprocess texts
    logger.info("Preprocessing training texts...")
    X_train_clean = preprocessor.preprocess_corpus(splits['X_train'])
    
    logger.info("Preprocessing validation texts...")
    X_val_clean = preprocessor.preprocess_corpus(splits['X_val'])
    
    logger.info("Preprocessing test texts...")
    X_test_clean = preprocessor.preprocess_corpus(splits['X_test'])
    
    # Vectorize
    logger.info("Vectorizing texts...")
    X_train_vec = preprocessor.fit_transform(X_train_clean)
    X_val_vec = preprocessor.transform(X_val_clean)
    X_test_vec = preprocessor.transform(X_test_clean)
    
    logger.info(f"Training features shape: {X_train_vec.shape}")
    logger.info(f"Validation features shape: {X_val_vec.shape}")
    logger.info(f"Test features shape: {X_test_vec.shape}")
    
    # Save vectorizer
    save_model(preprocessor.vectorizer, WIKIPEDIA_VECTORIZER_PATH)
    
    # Print statistics
    stats = data_module.get_data_stats()
    logger.info(f"Data statistics: {stats}")
    
    return {
        'X_train': X_train_vec,
        'X_val': X_val_vec,
        'X_test': X_test_vec,
        'y_train': splits['y_train'],
        'y_val': splits['y_val'],
        'y_test': splits['y_test'],
        'preprocessor': preprocessor
    }


def test_single_text():
    """
    Test preprocessing on a single text sample.
    """
    logger.info("=" * 50)
    logger.info("SINGLE TEXT PREPROCESSING TEST")
    logger.info("=" * 50)
    
    preprocessor = DataPreprocessor()
    
    # Test samples
    samples = [
        "Hey @user, check out this link: https://example.com #awesome",
        "You are such a loser!!! I hate you!!!",
        "This is a normal, friendly message."
    ]
    
    for i, text in enumerate(samples, 1):
        logger.info(f"\nSample {i}:")
        logger.info(f"Original: {text}")
        cleaned = preprocessor.preprocess_text(text)
        logger.info(f"Cleaned: {cleaned}")


if __name__ == '__main__':
    # Test single text preprocessing
    test_single_text()
    
    # Uncomment below when you have the datasets ready
    # preprocess_twitter_data()
    # preprocess_wikipedia_data()
