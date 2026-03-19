
import sys
sys.path.insert(0, '.')

from src.services import PredictionService
from src.utils import setup_logger

# Setup logging
logger = setup_logger('test_prediction_service', 'logs')

print("=" * 70)
print(" " * 15 + "PREDICTION SERVICE TEST")
print("=" * 70)

# Initialize service
print("\nInitializing PredictionService...")
service = PredictionService()
print("✓ Service initialized successfully\n")

# Test cases
test_cases = [
    {
        'text': 'Having a great day! Thanks everyone!',
        'source': 'twitter',
        'expected': 0
    },
    {
        'text': 'You are terrible and I hate you',
        'source': 'twitter',
        'expected': 1
    },
    {
        'text': 'This is a helpful edit to the article',
        'source': 'wikipedia',
        'expected': 0
    },
    {
        'text': 'Stop vandalizing you moron',
        'source': 'wikipedia',
        'expected': 1
    },
    {
        'text': 'You are such a loser',
        'source': 'auto',
        'expected': 1
    },
    {
        'text': 'Great work on this project!',
        'source': 'auto',
        'expected': 0
    }
]

print("=" * 70)
print("RUNNING TEST CASES")
print("=" * 70)

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}/{len(test_cases)}")
    print(f"Text: \"{test['text']}\"")
    print(f"Source: {test['source']}")
    
    try:
        result = service.predict(test['text'], test['source'])
        
        # Check if prediction matches expected
        if result['prediction'] == test['expected']:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"{status}")
        print(f"  Prediction: {result['label']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Detected Source: {result['source_type']}")
        print(f"  Latency: {result['latency_ms']:.2f}ms")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        failed += 1

# Test batch prediction
print("\n" + "=" * 70)
print("TESTING BATCH PREDICTION")
print("=" * 70)

batch_texts = [
    "Thanks for your help!",
    "You're an idiot",
    "Nice weather today"
]

print(f"\nPredicting {len(batch_texts)} texts...")
batch_results = service.predict_batch(batch_texts, 'auto')

for i, result in enumerate(batch_results, 1):
    if 'error' in result:
        print(f"\n{i}. ERROR: {result['error']}")
    else:
        print(f"\n{i}. \"{result['text']}\"")
        print(f"   → {result['label']} ({result['confidence']:.2%})")

# Test model info
print("\n" + "=" * 70)
print("MODEL INFORMATION")
print("=" * 70)

model_info = service.get_model_info()
print("\nTwitter Model:")
print(f"  Type: {model_info['twitter_model']['type']}")
print(f"  Kernel: {model_info['twitter_model']['kernel']}")
print(f"  Classes: {', '.join(model_info['twitter_model']['classes'])}")

print("\nWikipedia Model:")
print(f"  Type: {model_info['wikipedia_model']['type']}")
print(f"  Estimators: {model_info['wikipedia_model']['n_estimators']}")
print(f"  Classes: {', '.join(model_info['wikipedia_model']['classes'])}")

print("\nPreprocessor:")
print(f"  Max Features: {model_info['preprocessor']['max_features']}")
print(f"  N-gram Range: {model_info['preprocessor']['ngram_range']}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"\nTotal Tests: {len(test_cases)}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")

if failed == 0:
    print("\n✓ ALL TESTS PASSED!")
    print("✓ PredictionService is working correctly")
    print("✓ Ready to start Flask API")
else:
    print(f"\n⚠ {failed} test(s) failed")

print("\n" + "=" * 70)
