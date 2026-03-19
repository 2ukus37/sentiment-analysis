"""
DataPreprocessor: Handles text normalization, cleaning, and vectorization
"""
import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import logging

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class DataPreprocessor:
    """
    Handles all text preprocessing steps for cyberbullying detection.
    Optimized for memory efficiency on 4GB RAM systems.
    """
    
    def __init__(self, use_count_vectorizer=False, max_features=5000, 
                 min_df=2, max_df=0.95, ngram_range=(1, 2)):
        """
        Initialize the preprocessor with vectorization settings.
        
        Args:
            use_count_vectorizer: If True, use CountVectorizer instead of TF-IDF
            max_features: Maximum vocabulary size (memory constraint)
            min_df: Minimum document frequency
            max_df: Maximum document frequency
            ngram_range: N-gram range for vectorization
        """
        self.use_count_vectorizer = use_count_vectorizer
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        
        # Initialize components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def clean_text(self, text):
        """
        Clean and normalize text data.
        
        Steps:
        1. Convert to lowercase
        2. Remove URLs
        3. Remove mentions (@username)
        4. Remove hashtags (#hashtag)
        5. Remove punctuation
        6. Remove extra whitespace
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags
        text = re.sub(r'#\w+', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def remove_stopwords(self, text):
        """
        Remove stopwords from text.
        
        Args:
            text: Cleaned text string
            
        Returns:
            Text with stopwords removed
        """
        words = text.split()
        filtered_words = [word for word in words if word not in self.stop_words]
        return ' '.join(filtered_words)
    
    def lemmatize_text(self, text):
        """
        Lemmatize words in text.
        
        Args:
            text: Text with stopwords removed
            
        Returns:
            Lemmatized text
        """
        words = text.split()
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)
    
    def preprocess_text(self, text):
        """
        Apply full preprocessing pipeline to a single text.
        
        Args:
            text: Raw text string
            
        Returns:
            Fully preprocessed text
        """
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        text = self.lemmatize_text(text)
        return text
    
    def preprocess_corpus(self, texts):
        """
        Apply preprocessing to a corpus of texts.
        
        Args:
            texts: List or Series of text strings
            
        Returns:
            List of preprocessed texts
        """
        self.logger.info(f"Preprocessing {len(texts)} texts...")
        preprocessed = [self.preprocess_text(text) for text in texts]
        self.logger.info("Preprocessing complete.")
        return preprocessed
    
    def fit_vectorizer(self, texts):
        """
        Fit the vectorizer on training texts.
        
        Args:
            texts: List of preprocessed texts
            
        Returns:
            self
        """
        if self.use_count_vectorizer:
            self.vectorizer = CountVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                ngram_range=self.ngram_range
            )
        else:
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                ngram_range=self.ngram_range
            )
        
        self.logger.info(f"Fitting vectorizer with max_features={self.max_features}...")
        self.vectorizer.fit(texts)
        self.logger.info(f"Vectorizer fitted. Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        
        return self
    
    def transform(self, texts):
        """
        Transform texts to feature vectors.
        
        Args:
            texts: List of preprocessed texts
            
        Returns:
            Sparse matrix of features
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted. Call fit_vectorizer first.")
        
        return self.vectorizer.transform(texts)
    
    def fit_transform(self, texts):
        """
        Fit vectorizer and transform texts in one step.
        
        Args:
            texts: List of preprocessed texts
            
        Returns:
            Sparse matrix of features
        """
        self.fit_vectorizer(texts)
        return self.transform(texts)
    
    def get_feature_names(self):
        """
        Get feature names from the vectorizer.
        
        Returns:
            List of feature names
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted.")
        
        return self.vectorizer.get_feature_names_out()
