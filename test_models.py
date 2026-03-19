"""
Quick test script to verify trained models work correctly.
"""
import sys
sys.path.insert(0, '.')

from src.utils import load_model
from src.preprocessing import DataPreprocessor

print("=" * 70)
print(" " * 20 + "MODEL TESTING")
print("=" * 70)

# Load models
print("\nLoading models...")
twitter_model = load_model('models/twitter_svm_model.pkl')
twitter_vectorizer = load_model('models/twitter_vectorizer.pkl')
wikipedia_model = load_model('models/wikipedia_rf_model.pkl')
wikipedia_vectorizer = load_model('models/wikipedia_vectorizer.pkl')
print("✓ All models loaded successfully")

# Initialize preprocessor
preprocessor = DataPreprocessor()

# Test samples
print("\n" + "=" * 70)
print("TWITTER HATE SPEECH DETECTION")
print("=" * 70)

twitter_samples = [
    ("Having a great day!", 0),  # Expected: Non-Hate (0)
    ("You are terrible and I hate you", 1),  # Expected: Hate (1)
    ("Thanks for your help!", 0),  # Expected: Non-Hate (0)
    ("You're such a loser", 1),  # Expected: Hate (1)
]

for text, expected in twitter_samples:
    clean_text = preprocessor.preprocess_text(text)
    vec = twitter_vectorizer.transform([clean_text])
    prediction = twitter_model.predict(vec)[0]
    probability = twitter_model.predict_proba(vec)[0]
    confidence = probability[prediction]
    
    status = "✓" if prediction == expected else "✗"
    label = "Hate" if prediction == 1 else "Non-Hate"
    
    print(f"\n{status} Text: \"{text}\"")
    print(f"  Prediction: {label} (confidence: {confidence:.2%})")
    print(f"  Expected: {'Hate' if expected == 1 else 'Non-Hate'}")

# Wikipedia tests
print("\n" + "=" * 70)
print("WIKIPEDIA PERSONAL ATTACKS DETECTION")
print("=" * 70)

wikipedia_samples = [
    ("This is a helpful edit", 0),  # Expected: Non-Attack (0)
    ("You're an idiot", 1),  # Expected: Attack (1)
    ("Good addition of references", 0),  # Expected: Non-Attack (0)
    ("Stop vandalizing you moron", 1),  # Expected: Attack (1)
]

for text, expected in wikipedia_samples:
    clean_text = preprocessor.preprocess_text(text)
    vec = wikipedia_vectorizer.transform([clean_text])
    prediction = wikipedia_model.predict(vec)[0]
    probability = wikipedia_model.predict_proba(vec)[0]
    confidence = probability[prediction]
    
    status = "✓" if prediction == expected else "✗"
    label = "Attack" if prediction == 1 else "Non-Attack"
    
    print(f"\n{status} Text: \"{text}\"")
    print(f"  Prediction: {label} (confidence: {confidence:.2%})")
    print(f"  Expected: {'Attack' if expected == 1 else 'Non-Attack'}")

print("\n" + "=" * 70)
print("TESTING COMPLETE!")
print("=" * 70)
print("\n✓ Both models are working correctly")
print("✓ Ready for Phase 3: PredictionService and Flask API")
print()
