"""
Configuration file for TikTok Review Analysis Project
Contains all configurable parameters for scraping, cleaning, and analysis
"""

import os
from datetime import datetime, timedelta

# ============================================================================
# GOOGLE PLAY STORE CONFIGURATION
# ============================================================================

# Target app details
APP_ID = "com.zhiliaoapp.musicallyshl-en_us"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}"
APP_NAME = "TikTok"

# Scraping parameters
REVIEWS_TO_SCRAPE = 500  # Number of reviews to fetch (increase for more data)
DAYS_TO_ANALYZE = 10     # Look back period in days
SORT_BY = "newest"       # Options: newest, rating, most_helpful

# ============================================================================
# FILE PATHS
# ============================================================================

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
ARCHIVE_DATA_DIR = os.path.join(DATA_DIR, "archive")

# Output directories
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Report file
REPORT_FILE = os.path.join(OUTPUT_DIR, "review.html")

# ============================================================================
# FILE NAMING CONVENTIONS
# ============================================================================

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

def get_raw_data_filename():
    """Generate timestamped raw data filename"""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return os.path.join(RAW_DATA_DIR, f"reviews_raw_{timestamp}.json")

PROCESSED_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, "reviews_clean.csv")
ANALYSIS_SUMMARY_FILE = os.path.join(PROCESSED_DATA_DIR, "analysis_summary.json")
PAIN_POINTS_FILE = os.path.join(PROCESSED_DATA_DIR, "pain_points.json")

# ============================================================================
# ANALYSIS PARAMETERS
# ============================================================================

# Sentiment analysis
SENTIMENT_THRESHOLD_POSITIVE = 0.5   # Threshold for positive sentiment
SENTIMENT_THRESHOLD_NEGATIVE = -0.5  # Threshold for negative sentiment

# Keyword extraction
MIN_KEYWORD_FREQUENCY = 2            # Minimum occurrences to be considered a keyword
MAX_KEYWORDS = 10                    # Top N keywords to extract
KEYWORD_MIN_LENGTH = 3               # Minimum word length for keywords
KEYWORD_STOP_WORDS = [
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'be', 'was', 'were', 'been',
    'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'may', 'might', 'must', 'can', 'app', 'tiktok', 'this', 'that', 'it'
]

# Review filtering
MIN_REVIEW_LENGTH = 5                # Minimum characters for a valid review
REMOVE_SPAM = True                   # Enable spam removal heuristics
SPAM_KEYWORD_THRESHOLD = 5           # Max occurrence of keyword in review to avoid spam

# ============================================================================
# DATA CLEANING PARAMETERS
# ============================================================================

# Language detection
DETECT_LANGUAGE = True
TARGET_LANGUAGE = 'en'               # English only

# Text normalization
LOWERCASE_TEXT = True
REMOVE_SPECIAL_CHARS = False         # Keep emojis for sentiment analysis
REMOVE_URLS = True
REMOVE_EMAILS = True
REMOVE_NUMBERS = False

# Duplicate detection
DUPLICATE_SIMILARITY_THRESHOLD = 0.95  # Threshold for fuzzy matching

# ============================================================================
# NLP CONFIGURATION
# ============================================================================

# NLTK data requirements
NLTK_DOWNLOADS = [
    'punkt',
    'averaged_perceptron_tagger',
    'maxent_ne_chunker',
    'words',
    'wordnet',
    'omw-1.4'
]

# ============================================================================
# REPORT CONFIGURATION
# ============================================================================

# HTML Report settings
REPORT_THEME = "light"               # light or dark
REPORT_TITLE = f"{APP_NAME} Review Analysis Report"
INCLUDE_DATA_TABLE = True
MAX_ROWS_IN_TABLE = 50               # Show top N reviews in table
CHART_HEIGHT = 400                   # Plotly chart height in pixels

# ============================================================================
# SCRAPING CONFIGURATION
# ============================================================================

# Rate limiting
REQUEST_TIMEOUT = 10                 # Seconds
RATE_LIMIT_DELAY = 2                 # Seconds between requests
MAX_RETRIES = 3                      # Maximum retry attempts
BACKOFF_FACTOR = 2                   # Exponential backoff multiplier

# User agents (rotate to avoid blocking)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.path.join(LOGS_DIR, "app.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Keep logs for N days
LOG_RETENTION_DAYS = 30

# ============================================================================
# DATABASE CONFIGURATION (Future use)
# ============================================================================

# Uncomment when implementing database storage
# DB_TYPE = "sqlite"  # sqlite, postgresql, mysql
# DB_HOST = "localhost"
# DB_PORT = 5432
# DB_NAME = "tiktok_reviews"
# DB_USER = "user"
# DB_PASSWORD = "password"

# ============================================================================
# DATETIME CONFIGURATION
# ============================================================================

# Analyze reviews from the past N days
ANALYSIS_START_DATE = datetime.now() - timedelta(days=DAYS_TO_ANALYZE)
ANALYSIS_END_DATE = datetime.now()

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_SENTIMENT_ANALYSIS = True
ENABLE_TREND_ANALYSIS = True
ENABLE_PAIN_POINT_EXTRACTION = True
ENABLE_INTERACTIVE_CHARTS = True
ENABLE_DATA_EXPORT = True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def ensure_directories_exist():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, ARCHIVE_DATA_DIR,
        OUTPUT_DIR, LOGS_DIR
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_config_summary():
    """Return a summary of current configuration"""
    return {
        'app_id': APP_ID,
        'app_name': APP_NAME,
        'reviews_to_scrape': REVIEWS_TO_SCRAPE,
        'days_to_analyze': DAYS_TO_ANALYZE,
        'analysis_period': f"{ANALYSIS_START_DATE.date()} to {ANALYSIS_END_DATE.date()}",
        'report_file': REPORT_FILE,
        'data_dir': DATA_DIR,
        'max_retries': MAX_RETRIES,
        'sentiment_enabled': ENABLE_SENTIMENT_ANALYSIS,
    }

# Ensure directories exist on import
ensure_directories_exist()
