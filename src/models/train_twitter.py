"""
Twitter SVM Model Training Script
Target: 96% test accuracy with optimized hyperparameters
"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
import numpy as np

from src.preprocessing import DataPreprocessor, DataModule
from src.models.evaluator import ModelEvaluator
from src.utils import setup_logger, save_model
from config.config import *


def train_twitter_svm():
    """
    Train SVM model on Twitter hate speech dataset with grid search.
    """
    # Setup logging
    logger = setup_logger('train_twitter', LOGS_DIR)
    
    logger.info("=" * 70)
    logger.info("TWITTER HATE SPEECH DETECTION - SVM TRAINING")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # Step 1: Load and prepare data
    logger.info("\n[1/6] Loading Twitter dataset...")
    data_module = DataModule(
        random_seed=RANDOM_SEED,
        test_size=TEST_SIZE,
        val_size=VAL_SIZE
    )
    
    try:
        df = data_module.load_twitter_data(TWITTER_DATA_PATH)
    except FileNotFoundError:
        logger.error(f"Dataset not found at {TWITTER_DATA_PATH}")
        logger.error("Please place twitter_hate_speech.csv in the data/ directory")
        return None
    
    # Prepare data
    texts, labels = data_module.prepare_data(df['tweet'], df['label'])
    splits = data_module.split_data(texts, labels, include_val=True)
    
    # Step 2: Preprocess texts
    logger.info("\n[2/6] Preprocessing texts...")
    preprocessor = DataPreprocessor(
        use_count_vectorizer=False,
        max_features=MAX_FEATURES,
        min_df=MIN_DF,
        max_df=MAX_DF,
        ngram_range=NGRAM_RANGE
    )
    
    logger.info("Cleaning training texts...")
    X_train_clean = preprocessor.preprocess_corpus(splits['X_train'])
    
    logger.info("Cleaning validation texts...")
    X_val_clean = preprocessor.preprocess_corpus(splits['X_val'])
    
    logger.info("Cleaning test texts...")
    X_test_clean = preprocessor.preprocess_corpus(splits['X_test'])
    
    # Step 3: Vectorize
    logger.info("\n[3/6] Vectorizing texts with TF-IDF...")
    X_train_vec = preprocessor.fit_transform(X_train_clean)
    X_val_vec = preprocessor.transform(X_val_clean)
    X_test_vec = preprocessor.transform(X_test_clean)
    
    logger.info(f"Training features shape: {X_train_vec.shape}")
    logger.info(f"Validation features shape: {X_val_vec.shape}")
    logger.info(f"Test features shape: {X_test_vec.shape}")
    
    # Save vectorizer
    save_model(preprocessor.vectorizer, TWITTER_VECTORIZER_PATH)
    
    # Step 4: Train SVM with Grid Search
    logger.info("\n[4/6] Training SVM with Grid Search...")
    logger.info(f"Hyperparameter grid: {TWITTER_SVM_PARAMS}")
    
    # Initialize SVM
    svm = SVC(probability=True, random_state=RANDOM_SEED, cache_size=500)
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        svm,
        TWITTER_SVM_PARAMS,
        cv=3,
        scoring='f1',
        n_jobs=-1,
        verbose=2
    )
    
    logger.info("Starting grid search (this may take several minutes)...")
    grid_search.fit(X_train_vec, splits['y_train'])
    
    logger.info(f"Best parameters: {grid_search.best_params_}")
    logger.info(f"Best cross-validation F1-score: {grid_search.best_score_:.4f}")
    
    # Get best model
    best_model = grid_search.best_estimator_
    
    # Step 5: Evaluate on validation set
    logger.info("\n[5/6] Evaluating on validation set...")
    evaluator_val = ModelEvaluator('twitter_svm_validation')
    
    y_val_pred = best_model.predict(X_val_vec)
    y_val_proba = best_model.predict_proba(X_val_vec)[:, 1]
    
    val_results = evaluator_val.generate_full_report(
        splits['y_val'],
        y_val_pred,
        y_val_proba,
        class_names=['Non-Hate', 'Hate'],
        save_dir=LOGS_DIR
    )
    
    # Step 6: Evaluate on test set
    logger.info("\n[6/6] Evaluating on test set...")
    evaluator_test = ModelEvaluator('twitter_svm_test')
    
    y_test_pred = best_model.predict(X_test_vec)
    y_test_proba = best_model.predict_proba(X_test_vec)[:, 1]
    
    test_results = evaluator_test.generate_full_report(
        splits['y_test'],
        y_test_pred,
        y_test_proba,
        class_names=['Non-Hate', 'Hate'],
        save_dir=LOGS_DIR
    )
    
    # Save model
    logger.info("\nSaving trained model...")
    save_model(best_model, TWITTER_MODEL_PATH)
    
    # Final summary
    elapsed_time = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"Total training time: {elapsed_time/60:.2f} minutes")
    logger.info(f"\nBest Model Configuration:")
    logger.info(f"  Kernel: {grid_search.best_params_['kernel']}")
    logger.info(f"  C: {grid_search.best_params_['C']}")
    logger.info(f"  Gamma: {grid_search.best_params_['gamma']}")
    logger.info(f"\nValidation Performance:")
    logger.info(f"  Accuracy: {val_results['accuracy']:.4f}")
    logger.info(f"  F1-Score: {val_results['f1_score']:.4f}")
    logger.info(f"\nTest Performance:")
    logger.info(f"  Accuracy: {test_results['accuracy']:.4f}")
    logger.info(f"  F1-Score: {test_results['f1_score']:.4f}")
    logger.info(f"  Precision: {test_results['precision']:.4f}")
    logger.info(f"  Recall: {test_results['recall']:.4f}")
    
    if test_results['accuracy'] >= 0.96:
        logger.info(f"\n✓ TARGET ACHIEVED! Test accuracy: {test_results['accuracy']:.4f} >= 0.96")
    else:
        logger.warning(f"\n⚠ Target not met. Test accuracy: {test_results['accuracy']:.4f} < 0.96")
        logger.info("Consider: increasing max_features, trying different kernels, or getting more data")
    
    logger.info(f"\nModel saved to: {TWITTER_MODEL_PATH}")
    logger.info(f"Vectorizer saved to: {TWITTER_VECTORIZER_PATH}")
    logger.info("=" * 70)
    
    return {
        'model': best_model,
        'vectorizer': preprocessor.vectorizer,
        'val_results': val_results,
        'test_results': test_results,
        'best_params': grid_search.best_params_
    }


if __name__ == '__main__':
    train_twitter_svm()
