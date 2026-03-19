"""
Test script for enhanced API endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_text_prediction():
    """Test enhanced text prediction with GPT."""
    print("\n=== Testing Enhanced Text Prediction ===")
    
    test_cases = [
        {"text": "You are stupid and worthless", "source_type": "twitter"},
        {"text": "Having a great day! Thanks everyone!", "source_type": "twitter"},
        {"text": "Stop vandalizing you moron", "source_type": "wikipedia"},
        {"text": "This is a helpful edit to the article", "source_type": "wikipedia"}
    ]
    
    for test_case in test_cases:
        print(f"\nText: {test_case['text']}")
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json=test_case
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Ensemble Label: {result.get('ensemble_label', 'N/A')}")
            print(f"Ensemble Confidence: {result.get('ensemble_confidence', 0):.2%}")
            print(f"ML Label: {result.get('ml_label', 'N/A')}")
            print(f"ML Confidence: {result.get('ml_confidence', 0):.2%}")
            if result.get('gpt_enabled'):
                print(f"GPT Confidence: {result.get('gpt_confidence', 0):.2%}")
                print(f"Models Agree: {result.get('models_agree', False)}")
        else:
            print(f"Error: {response.json()}")

def test_batch_prediction():
    """Test batch prediction."""
    print("\n=== Testing Batch Prediction ===")
    
    texts = [
        "You are terrible",
        "Have a nice day",
        "Stop being an idiot",
        "Great contribution to the discussion"
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/predict/batch",
        json={"texts": texts, "source_type": "auto"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Count: {result['count']}")
        for i, pred in enumerate(result['results']):
            label = pred.get('ensemble_label', pred.get('label', 'N/A'))
            confidence = pred.get('ensemble_confidence', pred.get('confidence', 0))
            print(f"{i+1}. {pred['text'][:50]} -> {label} ({confidence:.2%})")
    else:
        print(f"Error: {response.json()}")

if __name__ == "__main__":
    try:
        test_health()
        test_text_prediction()
        test_batch_prediction()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
