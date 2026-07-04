#!/usr/bin/env python
"""
Script 2: Clean and preprocess review data
Removes duplicates, validates, and standardizes review data
"""

import json
import pandas as pd
import sys
from datetime import datetime
from typing import List, Dict
from utils.logger import setup_logger
from utils.scraper_utils import load_reviews_from_json
from utils.analysis_utils import is_likely_spam, detect_language
from config import (
    RAW_DATA_DIR, PROCESSED_DATA_FILE, PROCESSED_DATA_DIR,
    REMOVE_SPAM, MIN_REVIEW_LENGTH, DETECT_LANGUAGE, TARGET_LANGUAGE,
    DUPLICATE_SIMILARITY_THRESHOLD, REMOVE_URLS, REMOVE_EMAILS
)
import os
import re

logger = setup_logger(__name__)

def load_raw_reviews():
    """
    Load the most recent raw review file
    
    Returns:
        List of reviews or None if failed
    """
    try:
        # Find the most recent raw data file
        raw_files = [f for f in os.listdir(RAW_DATA_DIR) if f.startswith('reviews_raw_')]
        if not raw_files:
            logger.error(f"No raw review files found in {RAW_DATA_DIR}")
            return None
        
        latest_file = sorted(raw_files)[-1]
        filepath = os.path.join(RAW_DATA_DIR, latest_file)
        
        logger.info(f"Loading raw reviews from: {latest_file}")
        reviews = load_reviews_from_json(filepath)
        return reviews
    
    except Exception as e:
        logger.error(f"Error loading raw reviews: {str(e)}", exc_info=True)
        return None

def clean_review_text(text: str) -> str:
    """
    Clean review text
    
    Args:
        text: Raw review text
    
    Returns:
        Cleaned text
    """
    text = str(text).strip()
    
    # Remove URLs
    if REMOVE_URLS:
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    
    # Remove email addresses
    if REMOVE_EMAILS:
        text = re.sub(r'\S+@\S+', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def remove_duplicates(reviews: List[Dict]) -> List[Dict]:
    """
    Remove duplicate reviews
    
    Args:
        reviews: List of reviews
    
    Returns:
        List of reviews without duplicates
    """
    logger.info(f"Checking for duplicates...")
    
    seen_reviews = set()
    unique_reviews = []
    duplicates_found = 0
    
    for review in reviews:
        review_id = review.get('reviewId')
        if review_id and review_id not in seen_reviews:
            seen_reviews.add(review_id)
            unique_reviews.append(review)
        else:
            duplicates_found += 1
    
    logger.info(f"Removed {duplicates_found} duplicate reviews")
    return unique_reviews

def clean_reviews(reviews: List[Dict]) -> List[Dict]:
    """
    Clean and preprocess reviews
    
    Args:
        reviews: List of raw reviews
    
    Returns:
        List of cleaned reviews
    """
    logger.info("="*80)
    logger.info("STEP 2: CLEANING AND PREPROCESSING DATA")
    logger.info("="*80)
    
    logger.info(f"Starting with {len(reviews)} reviews")
    
    # Remove duplicates
    reviews = remove_duplicates(reviews)
    
    cleaned_reviews = []
    removed_count = 0
    
    for idx, review in enumerate(reviews):
        try:
            # Extract content
            content = review.get('content', '').strip()
            
            # Skip empty reviews
            if not content or len(content) < MIN_REVIEW_LENGTH:
                removed_count += 1
                continue
            
            # Clean text
            content = clean_review_text(content)
            
            # Language detection
            if DETECT_LANGUAGE:
                lang = detect_language(content)
                if lang != TARGET_LANGUAGE:
                    removed_count += 1
                    continue
            
            # Spam detection
            if REMOVE_SPAM:
                if is_likely_spam(content, review.get('score', 3)):
                    removed_count += 1
                    continue
            
            # Create cleaned review
            cleaned_review = {
                'review_id': review.get('reviewId', ''),
                'user_name': review.get('userName', 'Anonymous'),
                'content': content,
                'score': int(review.get('score', 3)),
                'review_date': review.get('at', datetime.now().isoformat()),
                'version': review.get('appVersion', 'Unknown'),
                'original_review': review
            }
            
            cleaned_reviews.append(cleaned_review)
        
        except Exception as e:
            logger.warning(f"Error cleaning review {idx}: {str(e)}")
            removed_count += 1
            continue
    
    logger.info(f"\nCleaning Summary:")
    logger.info(f"  Original reviews: {len(reviews)}")
    logger.info(f"  Cleaned reviews: {len(cleaned_reviews)}")
    logger.info(f"  Removed: {removed_count}")
    
    return cleaned_reviews

def save_cleaned_reviews(reviews: List[Dict]) -> bool:
    """
    Save cleaned reviews to CSV
    
    Args:
        reviews: List of cleaned reviews
    
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'review_id': r['review_id'],
                'user_name': r['user_name'],
                'content': r['content'],
                'score': r['score'],
                'review_date': r['review_date'],
                'version': r['version']
            }
            for r in reviews
        ])
        
        # Save to CSV
        df.to_csv(PROCESSED_DATA_FILE, index=False, encoding='utf-8')
        logger.info(f"✓ Saved {len(df)} cleaned reviews to {PROCESSED_DATA_FILE}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error saving cleaned reviews: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    try:
        # Load raw reviews
        reviews = load_raw_reviews()
        if not reviews:
            logger.error("Failed to load raw reviews")
            sys.exit(1)
        
        # Clean reviews
        cleaned_reviews = clean_reviews(reviews)
        if not cleaned_reviews:
            logger.error("No reviews survived cleaning!")
            sys.exit(1)
        
        # Save cleaned reviews
        if save_cleaned_reviews(cleaned_reviews):
            logger.info("\n✓ Data cleaning completed successfully!")
            logger.info(f"Ready for next step: sentiment analysis")
            sys.exit(0)
        else:
            logger.error("\n✗ Failed to save cleaned reviews!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\nCleaning interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
