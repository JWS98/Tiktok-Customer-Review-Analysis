#!/usr/bin/env python
"""
Script 1: Scrape TikTok reviews from Google Play Store
Fetches the past 10 days of reviews and saves them as raw JSON
"""

import json
import sys
from datetime import datetime
from google_play_scraper import app, reviews_all
from utils.logger import setup_logger
from utils.scraper_utils import (
    save_reviews_to_json, filter_reviews_by_date, validate_review, RateLimiter
)
from config import (
    APP_ID, REVIEWS_TO_SCRAPE, DAYS_TO_ANALYZE, SORT_BY, 
    get_raw_data_filename, RAW_DATA_DIR
)
import os

logger = setup_logger(__name__)

def scrape_reviews():
    """
    Scrape reviews from Google Play Store
    
    Returns:
        List of review dictionaries or None if failed
    """
    logger.info("="*80)
    logger.info("STEP 1: SCRAPING REVIEWS FROM GOOGLE PLAY STORE")
    logger.info("="*80)
    
    try:
        logger.info(f"Target App ID: {APP_ID}")
        logger.info(f"Reviews to fetch: {REVIEWS_TO_SCRAPE}")
        logger.info(f"Sort by: {SORT_BY}")
        
        # Get app info
        try:
            app_info = app(APP_ID, lang='en', country='us')
            logger.info(f"App Name: {app_info['title']}")
            logger.info(f"Current Rating: {app_info['score']}")
        except Exception as e:
            logger.warning(f"Could not fetch app info: {str(e)}")
        
        # Fetch reviews
        logger.info("Fetching reviews...")
        reviews_list = []
        
        # Using generator to fetch reviews
        for review in reviews_all(APP_ID, lang='en', country='us', sort=SORT_BY):
            reviews_list.append(review)
            if len(reviews_list) >= REVIEWS_TO_SCRAPE:
                break
            
            # Progress indicator
            if len(reviews_list) % 50 == 0:
                logger.info(f"Fetched {len(reviews_list)} reviews...")
        
        logger.info(f"Total reviews fetched: {len(reviews_list)}")
        
        # Filter by date
        filtered_reviews = filter_reviews_by_date(reviews_list, DAYS_TO_ANALYZE)
        logger.info(f"Reviews from past {DAYS_TO_ANALYZE} days: {len(filtered_reviews)}")
        
        # Validate reviews
        valid_reviews = [r for r in filtered_reviews if validate_review(r)]
        logger.info(f"Valid reviews after validation: {len(valid_reviews)}")
        
        if not valid_reviews:
            logger.error("No valid reviews found!")
            return None
        
        # Save to JSON
        output_file = get_raw_data_filename()
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        if save_reviews_to_json(valid_reviews, output_file):
            logger.info(f"✓ Scraping completed successfully!")
            logger.info(f"✓ Saved {len(valid_reviews)} reviews to {output_file}")
            return valid_reviews
        else:
            logger.error("Failed to save reviews to JSON")
            return None
    
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    try:
        reviews = scrape_reviews()
        if reviews:
            logger.info("\n✓ Scraping step completed successfully!")
            logger.info(f"Ready for next step: data cleaning")
            sys.exit(0)
        else:
            logger.error("\n✗ Scraping failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
