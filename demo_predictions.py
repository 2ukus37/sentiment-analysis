"""
Live demonstration of the Cyberbullying Detection System.
Shows various test cases with detailed results.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_prediction(text, result):
    """Print a formatted prediction result."""
    print(f"\n📝 Text: \"{text}\"")
    print(f"   └─ Ensemble: {result['ensemble_label']} ({result['ensemble_confidence']*100:.1f}%)")
    print(f"   └─ ML Model: {result['ml_label']} ({result['ml_confidence']*100:.1f}%)")
    if result.get('gpt_enabled'):
        print(f"   └─ GPT: {result['gpt_confidence']*100:.1f}%")
        agree = "✅ Agree" if result['models_agree'] else "⚠️ Disagree"
        print(f"   └─ Models: {agree}")
    print(f"   └─ Source: {result['source_type'].title()}")
    print(f"   └─ Time: {result['latency_ms']:.2f}ms")

def main():
    print_header("🛡️ CYBERBULLYING DETECTION SYSTEM - LIVE DEMO")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Server: {BASE_URL}")
    
    # Check health
    print_header("1️⃣ HEALTH CHECK")
    health = requests.get(f"{BASE_URL}/api/health").json()
    print(f"✅ Status: {health['status']}")
    print(f"✅ Version: {health['version']}")
    print(f"✅ ML Service: {health['services']['ml_service']}")
    print(f"✅ GPT Service: {health['services']['gpt_service']}")
    print(f"✅ GPT Model: {health['services']['gpt_model']}")
    
    # Test cases
    print_header("2️⃣ TWITTER / SOCIAL MEDIA TESTS")
    
    twitter_tests = [
        "I love this community! Everyone is so helpful and kind.",
        "You're an idiot and nobody likes you.",
        "@user Thanks for the great advice! Really appreciate it.",
        "Go kill yourself you worthless piece of trash.",
        "Having an amazing day! #blessed #grateful",
        "I hope you die in a fire you stupid moron."
    ]
    
    for text in twitter_tests:
        response = requests.post(f"{BASE_URL}/api/predict", json={
            'text': text,
            'source_type': 'twitter'
        })
        if response.status_code == 200:
            print_prediction(text, response.json())
    
    print_header("3️⃣ WIKIPEDIA / FORUM TESTS")
    
    wikipedia_tests = [
        "This is a well-researched edit with proper citations.",
        "Stop vandalizing the page you incompetent fool.",
        "I disagree with this edit, but I respect your perspective.",
        "You're a complete idiot who doesn't know anything.",
        "Great contribution! This really improves the article.",
        "Revert this garbage immediately, you troll."
    ]
    
    for text in wikipedia_tests:
        response = requests.post(f"{BASE_URL}/api/predict", json={
            'text': text,
            'source_type': 'wikipedia'
        })
        if response.status_code == 200:
            print_prediction(text, response.json())
    
    print_header("4️⃣ AUTO-DETECTION TESTS")
    
    auto_tests = [
        "@user #happy Great post! Love it!",  # Should detect Twitter
        "This edit needs more reliable sources.",  # Should detect Wikipedia
        "You suck and everyone hates you!",  # Generic hate
        "Thank you for your thoughtful contribution."  # Generic positive
    ]
    
    for text in auto_tests:
        response = requests.post(f"{BASE_URL}/api/predict", json={
            'text': text,
            'source_type': 'auto'
        })
        if response.status_code == 200:
            result = response.json()
            print_prediction(text, result)
            print(f"   └─ 🎯 Auto-detected as: {result['source_type'].title()}")
    
    print_header("5️⃣ BATCH PROCESSING TEST")
    
    batch_texts = [
        "You're amazing!",
        "I hate you so much.",
        "Great work on this project!",
        "Kill yourself loser."
    ]
    
    response = requests.post(f"{BASE_URL}/api/predict/batch", json={
        'texts': batch_texts,
        'source_type': 'auto'
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📦 Processed {result['count']} texts:")
        for i, pred in enumerate(result['results'], 1):
            label = pred['ensemble_label']
            conf = pred['ensemble_confidence'] * 100
            emoji = "🔴" if "Hate" in label or "Attack" in label else "🟢"
            print(f"   {i}. {emoji} \"{pred['text'][:50]}...\" → {label} ({conf:.1f}%)")
    
    print_header("✅ DEMO COMPLETE")
    print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🌐 Web Interface: http://localhost:5000")
    print("📚 Documentation: See FINAL_SUMMARY.md")
    print("🧪 Run tests: python test_enhanced_api.py")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the server is running: .\\start_enhanced_api.bat")
