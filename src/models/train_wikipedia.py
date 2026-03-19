
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import numpy as np
import matplotlib.pyplot as plt

from src.preprocessing import DataPreprocessor, DataModule
from src.models.evaluator import ModelEvaluator
from src.utils import setup_logger, save_model
from config.config import *


def plot_feature_importance(model, feature_names, top_n=20, save_path=None):
    """
    Plot top N most important features.
    
    Args:
        model: Trained Random Forest model
        feature_names: List of feature names
        top_n: Number of top features to display
        save_path: Path to save the plot
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]
    
    plt.figure(figsize=(10, 8))
    plt.title(f'Top {top_n} Feature Importances')
    plt.barh(range(top_n), importances[indices])
    plt.yticks(range(top_n), [feature_names[i] for i in indices])
    plt.xlabel('Importance')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.close()


def train_wikipedia_rf():
    """
    Train Random Forest model on Wikipedia personal attacks dataset with grid search.
    """
    # Setup logging
    logger = setup_logger('train_wikipedia', LOGS_DIR)
    
    logger.info("=" * 70)
    logger.info("WIKIPEDIA PERSONAL ATTACKS DETECTION - RANDOM FOREST TRAINING")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # Step 1: Load and prepare data
    logger.info("\n[1/6] Loading Wikipedia dataset...")
    data_module = DataModule(
        random_seed=RANDOM_SEED,
        test_size=TEST_SIZE,
        val_size=VAL_SIZE
    )
    
    try:
        df = data_module.load_wikipedia_data(WIKIPEDIA_DATA_PATH)
    except FileNotFoundError:
        logger.error(f"Dataset not found at {WIKIPEDIA_DATA_PATH}")
        logger.error("Please place wikipedia_attacks.csv in the data/ directory")
        return None
    
    # Prepare data
    texts, labels = data_module.prepare_data(df['comment'], df['attack'])
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
    save_model(preprocessor.vectorizer, WIKIPEDIA_VECTORIZER_PATH)
    
    # Step 4: Train Random Forest with Grid Search
    logger.info("\n[4/6] Training Random Forest with Grid Search...")
    logger.info(f"Hyperparameter grid: {WIKIPEDIA_RF_PARAMS}")
    
    # Initialize Random Forest
    rf = RandomForestClassifier(
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbose=1
    )
    
    # Grid search with cross-validation
    grid_search = GridSearchCV(
        rf,
        WIKIPEDIA_RF_PARAMS,
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
    evaluator_val = ModelEvaluator('wikipedia_rf_validation')
    
    y_val_pred = best_model.predict(X_val_vec)
    y_val_proba = best_model.predict_proba(X_val_vec)[:, 1]
    
    val_results = evaluator_val.generate_full_report(
        splits['y_val'],
        y_val_pred,
        y_val_proba,
        class_names=['Non-Attack', 'Attack'],
        save_dir=LOGS_DIR
    )
    
    # Step 6: Evaluate on test set
    logger.info("\n[6/6] Evaluating on test set...")
    evaluator_test = ModelEvaluator('wikipedia_rf_test')
    
    y_test_pred = best_model.predict(X_test_vec)
    y_test_proba = best_model.predict_proba(X_test_vec)[:, 1]
    
    test_results = evaluator_test.generate_full_report(
        splits['y_test'],
        y_test_pred,
        y_test_proba,
        class_names=['Non-Attack', 'Attack'],
        save_dir=LOGS_DIR
    )
    
    # Feature importance analysis
    logger.info("\nAnalyzing feature importance...")
    feature_names = preprocessor.get_feature_names()
    importance_path = os.path.join(LOGS_DIR, 'wikipedia_rf_feature_importance.png')
    plot_feature_importance(best_model, feature_names, top_n=20, save_path=importance_path)
    logger.info(f"Feature importance plot saved to {importance_path}")
    
    # Log top features
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    logger.info("\nTop 10 Most Important Features:")
    for i, idx in enumerate(indices, 1):
        logger.info(f"  {i}. {feature_names[idx]}: {importances[idx]:.4f}")
    
    # Save model
    logger.info("\nSaving trained model...")
    save_model(best_model, WIKIPEDIA_MODEL_PATH)
    
    # Final summary
    elapsed_time = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"Total training time: {elapsed_time/60:.2f} minutes")
    logger.info(f"\nBest Model Configuration:")
    logger.info(f"  n_estimators: {grid_search.best_params_['n_estimators']}")
    logger.info(f"  max_depth: {grid_search.best_params_['max_depth']}")
    logger.info(f"  min_samples_split: {grid_search.best_params_['min_samples_split']}")
    logger.info(f"\nValidation Performance:")
    logger.info(f"  Accuracy: {val_results['accuracy']:.4f}")
    logger.info(f"  F1-Score: {val_results['f1_score']:.4f}")
    logger.info(f"\nTest Performance:")
    logger.info(f"  Accuracy: {test_results['accuracy']:.4f}")
    logger.info(f"  F1-Score: {test_results['f1_score']:.4f}")
    logger.info(f"  Precision: {test_results['precision']:.4f}")
    logger.info(f"  Recall: {test_results['recall']:.4f}")
    
    if test_results['accuracy'] >= 0.99:
        logger.info(f"\n✓ TARGET ACHIEVED! Test accuracy: {test_results['accuracy']:.4f} >= 0.99")
    else:
        logger.warning(f"\n⚠ Target not met. Test accuracy: {test_results['accuracy']:.4f} < 0.99")
        logger.info("Consider: increasing n_estimators, adjusting max_depth, or getting more data")
    
    logger.info(f"\nModel saved to: {WIKIPEDIA_MODEL_PATH}")
    logger.info(f"Vectorizer saved to: {WIKIPEDIA_VECTORIZER_PATH}")
    logger.info("=" * 70)
    
    return {
        'model': best_model,
        'vectorizer': preprocessor.vectorizer,
        'val_results': val_results,
        'test_results': test_results,
        'best_params': grid_search.best_params_
    }


if __name__ == '__main__':
    train_wikipedia_rf()
