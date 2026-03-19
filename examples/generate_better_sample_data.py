"""
Generate improved sample datasets with more diversity.
"""
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import DATA_DIR

def generate_twitter_improved(n_samples=2000, save=True):
    """Generate improved Twitter dataset with more diversity."""
    print(f"Generating {n_samples} improved Twitter samples...")
    
    # More diverse non-hate samples
    non_hate_templates = [
        "Having a great day today",
        "Thanks for your help",
        "I appreciate your support",
        "This is really helpful",
        "Great work everyone",
        "Love this community",
        "Excited about the news",
        "Beautiful weather today",
        "Happy to be here",
        "Looking forward to it",
        "That's a good point",
        "I agree with you",
        "Nice to meet you",
        "Congratulations on your success",
        "Well done",
        "Keep up the good work",
        "This made my day",
        "Feeling blessed",
        "So grateful for this",
        "Amazing opportunity",
        "Proud of you",
        "You're doing great",
        "This is awesome",
        "Love your work",
        "Fantastic job",
        "Really appreciate it",
        "Thank you so much",
        "This is wonderful",
        "Great idea",
        "Brilliant suggestion",
        "I support this",
        "Totally agree",
        "Makes sense to me",
        "Good thinking",
        "Smart move",
        "Wise decision",
        "Excellent point",
        "Very insightful",
        "Interesting perspective",
        "Thanks for sharing"
    ]
    
    # More diverse hate speech samples
    hate_templates = [
        "You're such a loser",
        "I hate you so much",
        "You're completely worthless",
        "Nobody likes you",
        "You're pathetic",
        "Go away nobody wants you",
        "You're disgusting",
        "I can't stand you",
        "You're the worst",
        "You should be ashamed",
        "You're an idiot",
        "You're so stupid",
        "You're trash",
        "You're a failure",
        "You're useless",
        "I wish you would disappear",
        "You're terrible at everything",
        "Everyone hates you",
        "You're a waste of space",
        "You're annoying",
        "Shut up loser",
        "You're so dumb",
        "You're a joke",
        "You're embarrassing",
        "You're a disgrace",
        "You're horrible",
        "You're the worst person",
        "You're so ugly",
        "You're a moron",
        "You're incompetent",
        "You're a coward",
        "You're weak",
        "You're pathetic and sad",
        "You're a complete idiot",
        "You're absolutely terrible",
        "I despise you",
        "You're worthless trash",
        "You're a total failure",
        "You're so annoying",
        "Get lost loser"
    ]
    
    # Add variations
    variations = ["", "!", "!!", "!!!", ".", "..."]
    
    data = []
    for i in range(n_samples):
        if i % 2 == 0:  # Non-hate
            text = np.random.choice(non_hate_templates)
            text = text + np.random.choice(variations)
            label = 0
        else:  # Hate
            text = np.random.choice(hate_templates)
            text = text + np.random.choice(variations)
            label = 1
        
        data.append({
            'id': i,
            'tweet': text,
            'label': label
        })
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Generated {len(df)} samples")
    print(f"Unique tweets: {df['tweet'].nunique()}")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    if save:
        filepath = os.path.join(DATA_DIR, 'twitter_hate_speech.csv')
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath}")
    
    return df


def generate_wikipedia_improved(n_samples=2000, save=True):
    """Generate improved Wikipedia dataset with more diversity."""
    print(f"\nGenerating {n_samples} improved Wikipedia samples...")
    
    # More diverse non-attack samples
    non_attack_templates = [
        "This is a helpful edit",
        "Good addition to the article",
        "Thanks for improving this",
        "Well written contribution",
        "This clarifies the topic",
        "Appreciate the detailed explanation",
        "The sources look reliable",
        "Nice work on the formatting",
        "This adds valuable information",
        "I agree with this change",
        "Good point about the context",
        "This section needs more citations",
        "I suggest we reorganize this",
        "The information here is accurate",
        "This improves readability",
        "Thanks for the correction",
        "Good catch on that error",
        "This makes it clearer",
        "Helpful reference added",
        "The grammar is better now",
        "This is more neutral",
        "Good balance of viewpoints",
        "The tone is appropriate",
        "This follows the guidelines",
        "Well researched content",
        "The citations are proper",
        "This is encyclopedic",
        "Good use of sources",
        "The structure is better",
        "This is well organized",
        "The facts are correct",
        "This is objective",
        "Good summary of the topic",
        "The writing is clear",
        "This is informative",
        "Well done on this section",
        "The references are good",
        "This is properly cited",
        "Good neutral point of view",
        "This is verifiable"
    ]
    
    # More diverse attack samples
    attack_templates = [
        "You're an idiot",
        "Stop vandalizing you moron",
        "You have no idea what you're talking about",
        "You're completely clueless",
        "This is garbage from a garbage person",
        "You're ruining Wikipedia",
        "You should be banned fool",
        "Your edits are worthless",
        "You're incompetent",
        "Stop wasting everyone's time",
        "You're a troll",
        "You're so stupid",
        "This is the dumbest thing ever",
        "You're clearly biased and ignorant",
        "You're a complete idiot",
        "Your contributions are terrible",
        "You don't belong here",
        "You're pathetic",
        "Go away you're annoying",
        "You're making this worse",
        "You're clueless about this topic",
        "You're wrong and stupid",
        "You're a waste of time",
        "You're destroying this article",
        "You're incompetent and biased",
        "You're a vandal",
        "You're ruining everything",
        "You're so ignorant",
        "You're a joke",
        "You're embarrassing yourself",
        "You're completely wrong",
        "You're making no sense",
        "You're being ridiculous",
        "You're a terrible editor",
        "You're hopeless",
        "You're useless here",
        "You're wasting our time",
        "You're clearly trolling",
        "You're so annoying",
        "You're a problem user"
    ]
    
    variations = ["", ".", "!", "!!", "..."]
    
    data = []
    for i in range(n_samples):
        if i % 2 == 0:  # Non-attack
            text = np.random.choice(non_attack_templates)
            text = text + np.random.choice(variations)
            attack = 0
        else:  # Attack
            text = np.random.choice(attack_templates)
            text = text + np.random.choice(variations)
            attack = 1
        
        data.append({
            'review_id': i,
            'comment': text,
            'year': np.random.choice([2015, 2016, 2017, 2018]),
            'attack': attack
        })
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Generated {len(df)} samples")
    print(f"Unique comments: {df['comment'].nunique()}")
    print(f"Label distribution:\n{df['attack'].value_counts()}")
    
    if save:
        filepath = os.path.join(DATA_DIR, 'wikipedia_attacks.csv')
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath}")
    
    return df


def main():
    print("=" * 60)
    print("IMPROVED SAMPLE DATA GENERATOR")
    print("=" * 60)
    print("\nGenerating datasets with more diverse vocabulary...")
    print()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    twitter_df = generate_twitter_improved(n_samples=2000, save=True)
    wikipedia_df = generate_wikipedia_improved(n_samples=2000, save=True)
    
    print("\n" + "=" * 60)
    print("IMPROVED SAMPLE DATA GENERATION COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  - {os.path.join(DATA_DIR, 'twitter_hate_speech.csv')}")
    print(f"  - {os.path.join(DATA_DIR, 'wikipedia_attacks.csv')}")
    print("\nNow retrain the models:")
    print("  python train_all_models.py")
    print()


if __name__ == '__main__':
    main()
