"""
Generate sample datasets for testing the training pipeline.
Use this if you don't have the actual datasets yet.
"""
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import DATA_DIR


def generate_twitter_sample(n_samples=1000, save=True):
    """
    Generate sample Twitter hate speech dataset.
    
    Args:
        n_samples: Number of samples to generate
        save: Whether to save to CSV
    """
    print(f"Generating {n_samples} Twitter samples...")
    
    # Sample non-hate tweets
    non_hate_samples = [
        "Having a great day today!",
        "Just finished a wonderful book",
        "Love spending time with friends",
        "Beautiful weather outside",
        "Excited for the weekend",
        "Thanks for your help!",
        "This is really interesting",
        "Great work on the project",
        "Looking forward to tomorrow",
        "Happy to be here",
        "Nice to meet you",
        "That's a good point",
        "I appreciate your feedback",
        "This is helpful information",
        "Enjoying my coffee this morning"
    ]
    
    # Sample hate speech tweets
    hate_samples = [
        "You are such a loser and nobody likes you",
        "I hate you so much you're terrible",
        "You're stupid and worthless",
        "Go away nobody wants you here",
        "You're the worst person ever",
        "I wish you would just disappear",
        "You're pathetic and disgusting",
        "Everyone thinks you're an idiot",
        "You should be ashamed of yourself",
        "You're a complete failure",
        "Nobody cares about your opinion loser",
        "You're so dumb it's unbelievable",
        "Get lost you're annoying",
        "You're trash and always will be",
        "I can't stand you at all"
    ]
    
    # Generate dataset
    data = []
    for i in range(n_samples):
        if i % 2 == 0:  # Non-hate
            text = np.random.choice(non_hate_samples)
            # Add some variation
            text = text + " " + np.random.choice(["😊", "👍", "❤️", "🎉", ""])
            label = 0
        else:  # Hate
            text = np.random.choice(hate_samples)
            # Add some variation
            text = text + " " + np.random.choice(["!!!", ".", "!", ""])
            label = 1
        
        data.append({
            'id': i,
            'tweet': text,
            'label': label
        })
    
    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Generated {len(df)} samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    if save:
        filepath = os.path.join(DATA_DIR, 'twitter_hate_speech.csv')
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath}")
    
    return df


def generate_wikipedia_sample(n_samples=1000, save=True):
    """
    Generate sample Wikipedia personal attacks dataset.
    
    Args:
        n_samples: Number of samples to generate
        save: Whether to save to CSV
    """
    print(f"\nGenerating {n_samples} Wikipedia samples...")
    
    # Sample non-attack comments
    non_attack_samples = [
        "This is a helpful edit to the article",
        "Thanks for improving the grammar",
        "Good addition of references",
        "This section needs more citations",
        "I suggest we reorganize this paragraph",
        "The information here is accurate",
        "Well written contribution",
        "This clarifies the topic nicely",
        "Appreciate the detailed explanation",
        "Good point about the historical context",
        "This edit improves readability",
        "The sources look reliable",
        "Nice work on the formatting",
        "This adds valuable information",
        "I agree with this change"
    ]
    
    # Sample attack comments
    attack_samples = [
        "You're an idiot who doesn't know anything",
        "Stop vandalizing this page you moron",
        "You're completely clueless about this topic",
        "What a stupid edit from a stupid person",
        "You should be banned for being so dumb",
        "This is garbage just like your other edits",
        "You're a troll and everyone knows it",
        "Your contributions are worthless",
        "Go away you're ruining Wikipedia",
        "You have no idea what you're talking about fool",
        "This is the dumbest thing I've ever read",
        "You're incompetent and shouldn't be editing",
        "What an idiotic comment",
        "You're clearly biased and ignorant",
        "Stop wasting everyone's time with your nonsense"
    ]
    
    # Generate dataset
    data = []
    for i in range(n_samples):
        if i % 2 == 0:  # Non-attack
            text = np.random.choice(non_attack_samples)
            attack = 0
        else:  # Attack
            text = np.random.choice(attack_samples)
            attack = 1
        
        data.append({
            'review_id': i,
            'comment': text,
            'year': np.random.choice([2015, 2016, 2017, 2018]),
            'attack': attack
        })
    
    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Generated {len(df)} samples")
    print(f"Label distribution:\n{df['attack'].value_counts()}")
    
    if save:
        filepath = os.path.join(DATA_DIR, 'wikipedia_attacks.csv')
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath}")
    
    return df


def main():
    """
    Generate both sample datasets.
    """
    print("=" * 60)
    print("SAMPLE DATA GENERATOR")
    print("=" * 60)
    print("\nThis will generate sample datasets for testing.")
    print("Note: These are synthetic samples for demonstration only.")
    print("For production, use real datasets from Kaggle or other sources.")
    print()
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate datasets
    twitter_df = generate_twitter_sample(n_samples=1000, save=True)
    wikipedia_df = generate_wikipedia_sample(n_samples=1000, save=True)
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA GENERATION COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  - {os.path.join(DATA_DIR, 'twitter_hate_speech.csv')}")
    print(f"  - {os.path.join(DATA_DIR, 'wikipedia_attacks.csv')}")
    print("\nYou can now run:")
    print("  python train_all_models.py")
    print("\nOr train individual models:")
    print("  python src/models/train_twitter.py")
    print("  python src/models/train_wikipedia.py")
    print()


if __name__ == '__main__':
    main()
