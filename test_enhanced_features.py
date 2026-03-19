"""
Test script for Phase 4 enhanced features.
Tests GPT integration and ensemble predictions.
"""
import sys
sys.path.insert(0, '.')

from src.services import EnhancedPredictionService
from src.utils import setup_logger

# Setup logging
logger = setup_logger('test_enhanced', 'logs')

print("=" * 70)
print(" " * 15 + "ENHANCED FEATURES TEST")
print("=" * 70)

# Initialize enhanced service
print("\nInitializing Enhanced Prediction Service...")
print("Note: GPT features require OpenRouter API key")
print()

# API key is already set in the code
service = EnhancedPredictionService()

# Check service status
status = service.get_service_status()
print("Service Status:")
print(f"  ML Service: {status['ml_service']}")
print(f"  GPT Service: {status['gpt_service']}")
print(f"  OCR Service: {status['ocr_service']}")
if status['gpt_model']:
    print(f"  GPT Model: {status['gpt_model']}")

print("\n" + "=" * 70)
print("TEST 1: Enhanced Prediction (ML + GPT)")
print("=" * 70)

test_text = "You are terrible and I hate you"
print(f"\nText: \"{test_text}\"")
print("Analyzing with both ML and GPT...")

result = service.predict_enhanced(test_text, source_type='auto', use_gpt=True)

print("\nResults:")
print(f"  ML Prediction: {result['ml_label']} ({result['ml_confidence']:.2%})")

if result.get('gpt_enabled'):
    print(f"  GPT Prediction: {'Cyberbullying' if result['gpt_prediction'] == 1 else 'Not Cyberbullying'} ({result['gpt_confidence']:.2%})")
    print(f"  GPT Severity: {result.get('gpt_severity', 'N/A')}")
    print(f"  GPT Type: {result.get('gpt_type', 'N/A')}")
    if result.get('gpt_reasoning'):
        print(f"  GPT Reasoning: {result['gpt_reasoning'][:100]}...")
    print(f"\n  Ensemble Prediction: {result['ensemble_label']} ({result['ensemble_confidence']:.2%})")
    print(f"  Models Agree: {result['models_agree']}")
else:
    print("  GPT: Not available (using ML only)")
    print(f"  Final Prediction: {result['ensemble_label']} ({result['ensemble_confidence']:.2%})")

print(f"\n  Total Latency: {result['total_latency_ms']:.2f}ms")

print("\n" + "=" * 70)
print("TEST 2: ML-Only Prediction (Faster)")
print("=" * 70)

test_text2 = "Thanks for your help!"
print(f"\nText: \"{test_text2}\"")
print("Analyzing with ML only...")

result2 = service.predict_enhanced(test_text2, source_type='auto', use_gpt=False)

print("\nResults:")
print(f"  ML Prediction: {result2['ml_label']} ({result2['ml_confidence']:.2%})")
print(f"  Final Prediction: {result2['ensemble_label']} ({result2['ensemble_confidence']:.2%})")
print(f"  Total Latency: {result2['total_latency_ms']:.2f}ms")

print("\n" + "=" * 70)
print("TEST 3: Batch Prediction")
print("=" * 70)

batch_texts = [
    "You're such a loser",
    "Great work everyone!",
    "I hate you so much"
]

print(f"\nProcessing {len(batch_texts)} texts...")
print("Using ML only for batch (GPT would be expensive)")

batch_results = service.predict_batch_enhanced(batch_texts, use_gpt=False)

for i, result in enumerate(batch_results, 1):
    print(f"\n{i}. \"{result['text']}\"")
    print(f"   → {result['ensemble_label']} ({result['ensemble_confidence']:.2%})")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("\n✓ Enhanced Prediction Service working")
print(f"✓ ML models: Available")
print(f"✓ GPT integration: {'Available' if status['gpt_service'] == 'available' else 'Disabled'}")
print(f"✓ OCR support: {'Available' if status['ocr_service'] == 'available' else 'Disabled'}")

if status['gpt_service'] == 'available':
    print("\n✓ Phase 4 features fully operational!")
    print("✓ Ready to start enhanced API server")
else:
    print("\n⚠ GPT features disabled (no API key or error)")
    print("  System works with ML models only")
    print("  To enable GPT: Set OPENROUTER_API_KEY environment variable")

print("\n" + "=" * 70)
