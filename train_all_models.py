"""
Unified training script for both Twitter SVM and Wikipedia Random Forest models.
Run this script to train both models sequentially.
"""
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.models.train_twitter import train_twitter_svm
from src.models.train_wikipedia import train_wikipedia_rf
from src.utils import setup_logger
from config.config import LOGS_DIR


def main():
    """
    Train both models and generate comprehensive reports.
    """
    logger = setup_logger('train_all_models', LOGS_DIR)
    
    print("\n" + "=" * 80)
    print(" " * 20 + "CYBERBULLYING DETECTION SYSTEM")
    print(" " * 25 + "MODEL TRAINING SUITE")
    print("=" * 80)
    
    total_start = time.time()
    
    # Train Twitter SVM
    print("\n\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + " " * 25 + "TRAINING MODEL 1/2" + " " * 35 + "█")
    print("█" + " " * 20 + "Twitter Hate Speech - SVM" + " " * 33 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    print("\n")
    
    twitter_results = None
    try:
        twitter_results = train_twitter_svm()
        if twitter_results:
            logger.info("✓ Twitter SVM training completed successfully")
        else:
            logger.error("✗ Twitter SVM training failed")
    except Exception as e:
        logger.error(f"✗ Error training Twitter SVM: {e}")
        import traceback
        traceback.print_exc()
    
    # Train Wikipedia Random Forest
    print("\n\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + " " * 25 + "TRAINING MODEL 2/2" + " " * 35 + "█")
    print("█" + " " * 17 + "Wikipedia Personal Attacks - RF" + " " * 30 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    print("\n")
    
    wikipedia_results = None
    try:
        wikipedia_results = train_wikipedia_rf()
        if wikipedia_results:
            logger.info("✓ Wikipedia RF training completed successfully")
        else:
            logger.error("✗ Wikipedia RF training failed")
    except Exception as e:
        logger.error(f"✗ Error training Wikipedia RF: {e}")
        import traceback
        traceback.print_exc()
    
    # Final summary
    total_time = time.time() - total_start
    
    print("\n\n")
    print("=" * 80)
    print(" " * 30 + "TRAINING SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Training Time: {total_time/60:.2f} minutes")
    
    print("\n" + "-" * 80)
    print("MODEL 1: Twitter Hate Speech Detection (SVM)")
    print("-" * 80)
    if twitter_results:
        test_acc = twitter_results['test_results']['accuracy']
        test_f1 = twitter_results['test_results']['f1_score']
        print(f"Status: {'✓ SUCCESS' if test_acc >= 0.96 else '⚠ NEEDS IMPROVEMENT'}")
        print(f"Test Accuracy: {test_acc:.4f} (Target: 0.96)")
        print(f"Test F1-Score: {test_f1:.4f}")
        print(f"Best Kernel: {twitter_results['best_params']['kernel']}")
        print(f"Best C: {twitter_results['best_params']['C']}")
    else:
        print("Status: ✗ FAILED - Check logs for details")
    
    print("\n" + "-" * 80)
    print("MODEL 2: Wikipedia Personal Attacks Detection (Random Forest)")
    print("-" * 80)
    if wikipedia_results:
        test_acc = wikipedia_results['test_results']['accuracy']
        test_f1 = wikipedia_results['test_results']['f1_score']
        print(f"Status: {'✓ SUCCESS' if test_acc >= 0.99 else '⚠ NEEDS IMPROVEMENT'}")
        print(f"Test Accuracy: {test_acc:.4f} (Target: 0.99)")
        print(f"Test F1-Score: {test_f1:.4f}")
        print(f"Best n_estimators: {wikipedia_results['best_params']['n_estimators']}")
        print(f"Best max_depth: {wikipedia_results['best_params']['max_depth']}")
    else:
        print("Status: ✗ FAILED - Check logs for details")
    
    print("\n" + "=" * 80)
    
    # Next steps
    if twitter_results and wikipedia_results:
        print("\n✓ ALL MODELS TRAINED SUCCESSFULLY!")
        print("\nNext Steps:")
        print("  1. Review evaluation plots in logs/ directory")
        print("  2. Check trained models in models/ directory")
        print("  3. Proceed to Phase 3: Implement PredictionService")
        print("  4. Build Flask API and Web UI")
    else:
        print("\n⚠ SOME MODELS FAILED TO TRAIN")
        print("\nTroubleshooting:")
        print("  1. Ensure datasets are in data/ directory")
        print("  2. Check data format matches requirements (see data/README.md)")
        print("  3. Review error logs in logs/ directory")
        print("  4. Verify sufficient memory (4GB+ recommended)")
    
    print("\n" + "=" * 80)
    print()


if __name__ == '__main__':
    main()
