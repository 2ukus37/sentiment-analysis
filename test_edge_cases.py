"""
Test edge cases for cyberbullying detection.
"""
import requests

def test_prediction(text, expected):
    """Test a single prediction."""
    response = requests.post('http://localhost:5000/api/predict', json={
        'text': text,
        'source_type': 'auto'
    })
    
    if response.status_code == 200:
        result = response.json()
        label = result['ensemble_label']
        confidence = result['ensemble_confidence'] * 100
        ml_pred = result['ml_label']
        gpt_pred = "Hate" if result['gpt_prediction'] == 1 else "Non-Hate"
        agree = "✅" if result['models_agree'] else "⚠️"
        
        correct = "✅" if expected.lower() in label.lower() else "❌"
        
        print(f"\n{correct} Text: \"{text[:60]}...\"" if len(text) > 60 else f"\n{correct} Text: \"{text}\"")
        print(f"   Expected: {expected}")
        print(f"   Got: {label} ({confidence:.1f}%)")
        print(f"   ML: {ml_pred} | GPT: {gpt_pred} | Agree: {agree}")
    else:
        print(f"\n❌ Error: {response.status_code}")

print("="*70)
print("  🧪 EDGE CASE TESTING")
print("="*70)

# Test cases
test_prediction("Having a great day! Thanks everyone! fuck you", "Hate")
test_prediction("You're so nice... NOT! You're an idiot", "Hate")
test_prediction("I love you... to die in a fire", "Hate")
test_prediction("Great job! Keep it up!", "Non-Hate")
test_prediction("fuck", "Hate")
test_prediction("You suck at everything", "Hate")
test_prediction("This is amazing work!", "Non-Hate")
test_prediction("Go kill yourself", "Hate")
test_prediction("I disagree with your opinion", "Non-Hate")
test_prediction("You're a fucking genius! (sarcasm)", "Hate")

print("\n" + "="*70)
print("  ✅ EDGE CASE TESTING COMPLETE")
print("="*70)
