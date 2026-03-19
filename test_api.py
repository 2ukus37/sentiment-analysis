"""
Test script for Flask API endpoints.
Run this after starting the API server.
"""
import requests
import json
import time

API_URL = "http://localhost:5000"

print("=" * 70)
print(" " * 20 + "API ENDPOINT TESTS")
print("=" * 70)

def test_health():
    """Test health check endpoint."""
    print("\n[1/5] Testing GET /api/health")
    try:
        response = requests.get(f"{API_URL}/api/health")
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_models():
    """Test models info endpoint."""
    print("\n[2/5] Testing GET /api/models")
    try:
        response = requests.get(f"{API_URL}/api/models")
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Twitter Model: {data['twitter_model']['type']}")
        print(f"✓ Wikipedia Model: {data['wikipedia_model']['type']}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_predict_twitter():
    """Test single prediction for Twitter."""
    print("\n[3/5] Testing POST /api/predict (Twitter)")
    try:
        payload = {
            "text": "You are terrible and I hate you",
            "source_type": "twitter"
        }
        response = requests.post(
            f"{API_URL}/api/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Prediction: {data['label']}")
        print(f"✓ Confidence: {data['confidence']:.2%}")
        print(f"✓ Latency: {data['latency_ms']}ms")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_predict_wikipedia():
    """Test single prediction for Wikipedia."""
    print("\n[4/5] Testing POST /api/predict (Wikipedia)")
    try:
        payload = {
            "text": "This is a helpful edit to the article",
            "source_type": "wikipedia"
        }
        response = requests.post(
            f"{API_URL}/api/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Prediction: {data['label']}")
        print(f"✓ Confidence: {data['confidence']:.2%}")
        print(f"✓ Latency: {data['latency_ms']}ms")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_batch_predict():
    """Test batch prediction."""
    print("\n[5/5] Testing POST /api/predict/batch")
    try:
        payload = {
            "texts": [
                "Thanks for your help!",
                "You're an idiot",
                "Nice weather today"
            ],
            "source_type": "auto"
        }
        response = requests.post(
            f"{API_URL}/api/predict/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Count: {data['count']} predictions")
        for i, result in enumerate(data['results'], 1):
            print(f"  {i}. {result['label']} ({result['confidence']:.2%})")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\nWaiting for API server to be ready...")
    time.sleep(2)
    
    results = []
    results.append(test_health())
    results.append(test_models())
    results.append(test_predict_twitter())
    results.append(test_predict_wikipedia())
    results.append(test_batch_predict())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {total - passed} ✗")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n✓ ALL API TESTS PASSED!")
        print("✓ Flask API is working correctly")
        print(f"✓ Web UI available at: {API_URL}")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to API server")
        print("Please start the server first with: python src/api/app.py")
        print("=" * 70)
