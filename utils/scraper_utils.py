"""
Utility functions for web scraping with rate limiting, retries, and error handling
"""

import time
import random
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, List, Dict, Any
from utils.logger import setup_logger
from config import (
    MAX_RETRIES, BACKOFF_FACTOR, REQUEST_TIMEOUT, RATE_LIMIT_DELAY, USER_AGENTS
)

logger = setup_logger(__name__)

class RateLimiter:
    """Rate limiter to control request frequency"""
    
    def __init__(self, delay: float = RATE_LIMIT_DELAY):
        self.delay = delay
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to maintain rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            wait_time = self.delay - elapsed
            time.sleep(wait_time)
        self.last_request_time = time.time()

def retry_on_exception(max_retries: int = MAX_RETRIES, backoff_factor: float = BACKOFF_FACTOR):
    """
    Decorator for automatic retry with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
        
        return wrapper
    return decorator

def get_random_user_agent() -> str:
    """Get a random user agent string"""
    return random.choice(USER_AGENTS)

def parse_review_date(date_str: str) -> Optional[datetime]:
    """
    Parse review date strings in various formats
    
    Args:
        date_str: Date string from review
    
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try to handle relative dates (e.g., "2 days ago")
    try:
        if "ago" in date_str.lower():
            if "day" in date_str.lower():
                days = int(date_str.lower().split()[0])
                return datetime.now() - timedelta(days=days)
            elif "hour" in date_str.lower():
                hours = int(date_str.lower().split()[0])
                return datetime.now() - timedelta(hours=hours)
            elif "minute" in date_str.lower():
                minutes = int(date_str.lower().split()[0])
                return datetime.now() - timedelta(minutes=minutes)
    except:
        pass
    
    logger.warning(f"Could not parse date: {date_str}")
    return None

def filter_reviews_by_date(reviews: List[Dict], days: int = 10) -> List[Dict]:
    """
    Filter reviews to only include those from the past N days
    
    Args:
        reviews: List of review dictionaries
        days: Number of days to look back
    
    Returns:
        Filtered list of reviews
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []
    
    for review in reviews:
        try:
            review_date = review.get('publishedDate')
            if isinstance(review_date, str):
                review_date = parse_review_date(review_date)
            
            if review_date and review_date >= cutoff_date:
                filtered.append(review)
            elif not review_date:
                # Keep reviews with unparseable dates
                filtered.append(review)
        except Exception as e:
            logger.warning(f"Error filtering review date: {str(e)}")
            filtered.append(review)
    
    logger.info(f"Filtered {len(reviews)} reviews to {len(filtered)} from past {days} days")
    return filtered

def validate_review(review: Dict) -> bool:
    """
    Validate that a review has required fields
    
    Args:
        review: Review dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['reviewId', 'userName', 'content', 'score', 'at']
    
    for field in required_fields:
        if field not in review or review[field] is None:
            return False
    
    # Check minimum review length
    if len(str(review.get('content', '')).strip()) < 5:
        return False
    
    return True

def save_reviews_to_json(reviews: List[Dict], filepath: str) -> bool:
    """
    Save reviews to JSON file with error handling
    
    Args:
        reviews: List of review dictionaries
        filepath: Output file path
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved {len(reviews)} reviews to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save reviews: {str(e)}")
        return False

def load_reviews_from_json(filepath: str) -> Optional[List[Dict]]:
    """
    Load reviews from JSON file with error handling
    
    Args:
        filepath: Input file path
    
    Returns:
        List of reviews or None if failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        logger.info(f"Loaded {len(reviews)} reviews from {filepath}")
        return reviews
    except Exception as e:
        logger.error(f"Failed to load reviews: {str(e)}")
        return None

def get_score_label(score: int) -> str:
    """
    Convert numeric rating to text label
    
    Args:
        score: Rating 1-5
    
    Returns:
        Text label for the rating
    """
    labels = {
        1: "Very Bad",
        2: "Bad",
        3: "Neutral",
        4: "Good",
        5: "Excellent"
    }
    return labels.get(score, "Unknown")
