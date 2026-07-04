"""
Utility functions for data analysis including sentiment analysis, keyword extraction, and NLP
"""

import re
import string
from typing import List, Dict, Tuple, Optional
from collections import Counter
import nltk
from textblob import TextBlob
from utils.logger import setup_logger
from config import (
    KEYWORD_STOP_WORDS, KEYWORD_MIN_LENGTH, MIN_KEYWORD_FREQUENCY,
    MAX_KEYWORDS, SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE
)

logger = setup_logger(__name__)

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class SentimentAnalyzer:
    """Analyze sentiment of text reviews"""
    
    @staticmethod
    def analyze(text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Args:
            text: Review text
        
        Returns:
            Dict with polarity, subjectivity, and label
        """
        try:
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity >= SENTIMENT_THRESHOLD_POSITIVE:
                label = "Positive"
            elif polarity <= SENTIMENT_THRESHOLD_NEGATIVE:
                label = "Negative"
            else:
                label = "Neutral"
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'label': label
            }
        except Exception as e:
            logger.warning(f"Error analyzing sentiment: {str(e)}")
            return {
                'polarity': 0,
                'subjectivity': 0.5,
                'label': "Unknown"
            }

class KeywordExtractor:
    """Extract keywords and phrases from reviews"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text for keyword extraction
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = MAX_KEYWORDS) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Review text
            top_n: Number of keywords to return
        
        Returns:
            List of keywords
        """
        try:
            cleaned_text = KeywordExtractor.clean_text(text)
            words = cleaned_text.split()
            
            # Filter words
            keywords = [
                word for word in words
                if (len(word) >= KEYWORD_MIN_LENGTH and 
                    word not in KEYWORD_STOP_WORDS)
            ]
            
            return keywords[:top_n]
        except Exception as e:
            logger.warning(f"Error extracting keywords: {str(e)}")
            return []
    
    @staticmethod
    def extract_phrases(text: str, min_length: int = 2, top_n: int = 5) -> List[str]:
        """
        Extract key phrases (2-3 word combinations)
        
        Args:
            text: Review text
            min_length: Minimum phrase word count
            top_n: Number of phrases to return
        
        Returns:
            List of phrases
        """
        try:
            cleaned_text = KeywordExtractor.clean_text(text)
            words = cleaned_text.split()
            
            # Generate n-grams
            phrases = []
            for n in range(2, 4):
                for i in range(len(words) - n + 1):
                    phrase = ' '.join(words[i:i+n])
                    # Filter out phrases with stop words
                    if not any(stop in phrase.split() for stop in KEYWORD_STOP_WORDS):
                        phrases.append(phrase)
            
            return phrases[:top_n]
        except Exception as e:
            logger.warning(f"Error extracting phrases: {str(e)}")
            return []

def get_most_common_keywords(reviews: List[Dict], top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Extract most common keywords across all reviews
    
    Args:
        reviews: List of review dictionaries with 'content' field
        top_n: Number of top keywords to return
    
    Returns:
        List of (keyword, frequency) tuples
    """
    all_keywords = []
    
    for review in reviews:
        text = review.get('content', '')
        keywords = KeywordExtractor.extract_keywords(text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    
    # Filter by minimum frequency
    filtered_keywords = [
        (kw, count) for kw, count in keyword_counts.most_common(top_n)
        if count >= MIN_KEYWORD_FREQUENCY
    ]
    
    logger.info(f"Extracted {len(filtered_keywords)} top keywords")
    return filtered_keywords

def identify_pain_points(reviews: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Identify top pain points from negative reviews
    
    Args:
        reviews: List of review dictionaries
        top_n: Number of pain points to return
    
    Returns:
        List of pain point dictionaries with keyword and frequency
    """
    # Filter negative reviews
    negative_reviews = [
        r for r in reviews
        if r.get('sentiment_label') == 'Negative'
    ]
    
    if not negative_reviews:
        logger.warning("No negative reviews found for pain point analysis")
        return []
    
    # Extract keywords from negative reviews
    all_keywords = []
    for review in negative_reviews:
        text = review.get('content', '')
        keywords = KeywordExtractor.extract_keywords(text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    pain_points = [
        {
            'keyword': kw,
            'frequency': count,
            'percentage': round((count / len(negative_reviews)) * 100, 2)
        }
        for kw, count in keyword_counts.most_common(top_n)
        if count >= MIN_KEYWORD_FREQUENCY
    ]
    
    logger.info(f"Identified {len(pain_points)} top pain points")
    return pain_points

def identify_praise_points(reviews: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Identify top praise points from positive reviews
    
    Args:
        reviews: List of review dictionaries
        top_n: Number of praise points to return
    
    Returns:
        List of praise point dictionaries with keyword and frequency
    """
    # Filter positive reviews
    positive_reviews = [
        r for r in reviews
        if r.get('sentiment_label') == 'Positive'
    ]
    
    if not positive_reviews:
        logger.warning("No positive reviews found for praise point analysis")
        return []
    
    # Extract keywords from positive reviews
    all_keywords = []
    for review in positive_reviews:
        text = review.get('content', '')
        keywords = KeywordExtractor.extract_keywords(text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    praise_points = [
        {
            'keyword': kw,
            'frequency': count,
            'percentage': round((count / len(positive_reviews)) * 100, 2)
        }
        for kw, count in keyword_counts.most_common(top_n)
        if count >= MIN_KEYWORD_FREQUENCY
    ]
    
    logger.info(f"Identified {len(praise_points)} top praise points")
    return praise_points

def calculate_review_stats(reviews: List[Dict]) -> Dict:
    """
    Calculate overall statistics for reviews
    
    Args:
        reviews: List of review dictionaries
    
    Returns:
        Dictionary with statistics
    """
    if not reviews:
        return {
            'total_reviews': 0,
            'avg_rating': 0,
            'avg_polarity': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_percentage': 0,
            'negative_percentage': 0,
            'neutral_percentage': 0,
        }
    
    total = len(reviews)
    
    # Rating stats
    ratings = [r.get('score', 3) for r in reviews]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Sentiment stats
    sentiments = [r.get('sentiment_label', 'Neutral') for r in reviews]
    positive_count = sentiments.count('Positive')
    negative_count = sentiments.count('Negative')
    neutral_count = sentiments.count('Neutral')
    
    # Polarity stats
    polarities = [r.get('sentiment_polarity', 0) for r in reviews]
    avg_polarity = sum(polarities) / len(polarities) if polarities else 0
    
    return {
        'total_reviews': total,
        'avg_rating': round(avg_rating, 2),
        'avg_polarity': round(avg_polarity, 3),
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'positive_percentage': round((positive_count / total) * 100, 2),
        'negative_percentage': round((negative_count / total) * 100, 2),
        'neutral_percentage': round((neutral_count / total) * 100, 2),
    }

def is_likely_spam(text: str, review_score: int) -> bool:
    """
    Detect likely spam reviews
    
    Args:
        text: Review text
        review_score: Rating 1-5
    
    Returns:
        True if likely spam, False otherwise
    """
    text = str(text).lower()
    
    # Spam indicators
    spam_patterns = [
        r'^\d+$',  # Only numbers
        r'(.)\1{4,}',  # Repeated characters
        r'http|www',  # URLs
        r'click|buy|download|subscribe',  # Commercial keywords
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, text):
            return True
    
    # Single emoji or special characters only
    if len(re.sub(r'[^\w\s]', '', text).strip()) < 3:
        return True
    
    return False

def detect_language(text: str) -> str:
    """
    Simple language detection (English vs non-English)
    
    Args:
        text: Review text
    
    Returns:
        Language code ('en' or 'other')
    """
    try:
        # Simple heuristic: count English words
        english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'
        }
        
        words = str(text).lower().split()
        english_count = sum(1 for w in words if w in english_words)
        
        return 'en' if english_count > len(words) * 0.1 else 'other'
    except:
        return 'en'  # Default to English
