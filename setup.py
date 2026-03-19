
import os
import subprocess
import sys


def create_directories():
 
    dirs = ['data', 'models', 'logs', 'static', 'templates']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def install_requirements():

    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False
    return True


def download_nltk_data():
    print("\nDownloading NLTK data...")
    try:
        import nltk
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        print("✓ NLTK data downloaded successfully")
    except Exception as e:
        print(f"✗ Error downloading NLTK data: {e}")
        return False
    return True


def download_spacy_model():
    print("\nDownloading spaCy model...")
    try:
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
        print("✓ spaCy model downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error downloading spaCy model: {e}")
        print("  You can manually install it later with: python -m spacy download en_core_web_sm")
        return False
    return True


def main():
    print("=" * 60)
    print("Cyberbullying Detection System - Setup")
    print("=" * 60)
    
    # Create directories
    print("\n[1/4] Creating directories...")
    create_directories()
    
    # Install requirements
    print("\n[2/4] Installing dependencies...")
    if not install_requirements():
        print("\n✗ Setup failed at dependency installation")
        return
    
    # Download NLTK data
    print("\n[3/4] Downloading NLTK data...")
    download_nltk_data()
    
    # Download spaCy model
    print("\n[4/4] Downloading spaCy model...")
    download_spacy_model()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Place your datasets in the data/ directory")
    print("2. Run preprocessing: python examples/preprocess_example.py")
    print("3. Train models: python src/models/train_twitter.py")
    print("4. Start API: python src/api/app.py")
    print("\nFor more information, see README.md")


if __name__ == '__main__':
    main()
