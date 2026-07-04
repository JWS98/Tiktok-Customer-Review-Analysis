# TikTok Customer Review Analysis

A comprehensive Python-based pipeline to scrape, clean, analyze, and visualize TikTok reviews from the Google Play Store.

## Overview

This project automates the collection and analysis of the past 10 days of TikTok customer reviews, extracting actionable insights about pain points, review trends, sentiment analysis, and key metrics.

## Features

- **Web Scraping**: Automatically scrapes reviews from Google Play Store
- **Data Cleaning**: Removes duplicates, standardizes formats, handles missing data
- **Sentiment Analysis**: Analyzes review sentiment (positive/negative/neutral)
- **Trend Analysis**: Identifies patterns and trends over the 10-day period
- **Pain Point Extraction**: Identifies most common customer complaints
- **Interactive Reports**: Generates beautiful HTML reports with interactive charts
- **Error Handling**: Robust retry logic and error recovery mechanisms

## Project Structure

```
Tiktok-Customer-Review-Analysis/
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── data/
│   ├── raw/                    # Raw scraped data
│   ├── processed/              # Cleaned data
│   └── archive/                # Historical data
├── scripts/
│   ├── 01_scrape_reviews.py    # Main scraper
│   ├── 02_clean_data.py        # Data cleaning
│   ├── 03_analyze_reviews.py   # Analysis & insights
│   └── 04_generate_report.py   # HTML report generation
├── output/
│   └── review.html             # Final report
├── logs/
│   └── app.log                 # Application logs
├── notebooks/
│   └── exploration.ipynb       # EDA (optional)
└── utils/
    ├── __init__.py
    ├── scraper_utils.py        # Helper functions
    ├── analysis_utils.py       # Analysis helpers
    └── logger.py               # Logging configuration
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JWS98/Tiktok-Customer-Review-Analysis.git
cd Tiktok-Customer-Review-Analysis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

## Usage

### Quick Start

Run the complete pipeline:
```bash
python main.py
```

This will:
1. Scrape the latest reviews from TikTok
2. Clean and standardize the data
3. Perform sentiment and trend analysis
4. Generate an interactive HTML report

### Manual Execution

Run individual scripts:

```bash
# 1. Scrape reviews
python scripts/01_scrape_reviews.py

# 2. Clean data
python scripts/02_clean_data.py

# 3. Analyze reviews
python scripts/03_analyze_reviews.py

# 4. Generate report
python scripts/04_generate_report.py
```

## Configuration

Edit `config.py` to customize:
- Number of reviews to scrape
- Number of days to analyze
- File paths
- Analysis parameters
- Report settings

## Output

After running the pipeline, you'll get:

- **`data/raw/`**: Raw scraped review JSON files
- **`data/processed/`**: Cleaned CSV files and analysis results
- **`output/review.html`**: Interactive HTML report with:
  - Key performance indicators
  - Rating distribution
  - Sentiment trends
  - Pain points analysis
  - Praise points analysis
  - Daily review volume
  - Detailed review tables

## Report Contents

The generated `review.html` includes:

1. **Executive Summary**: High-level metrics
2. **KPI Cards**: Average rating, total reviews, sentiment breakdown
3. **Visualizations**:
   - Rating distribution histogram
   - Sentiment trend over time
   - Top pain points (bar chart)
   - Top praise points (bar chart)
   - Daily review volume (area chart)
4. **Data Tables**: Sortable/filterable review details
5. **Insights & Recommendations**: Actionable recommendations

## Logs

All activity is logged to `logs/app.log` for debugging and monitoring.

## Error Handling

The pipeline includes:
- Automatic retry logic with exponential backoff
- Network error recovery
- Data validation checks
- Comprehensive error logging

## Limitations & Notes

- Respects Google Play Store rate limiting
- Requires internet connection
- Reviews are in English (filter applied)
- Sentiment analysis accuracy depends on text clarity
- Some reviews may contain emojis/special characters

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Multi-app comparison analysis
- [ ] Scheduled automatic scraping (cron jobs)
- [ ] Database storage (SQLite/PostgreSQL)
- [ ] API endpoint for real-time insights
- [ ] Advanced NLP (named entity recognition, aspect-based sentiment)
- [ ] Competitor analysis
- [ ] Predictive analytics

## Dependencies

See `requirements.txt` for the full list. Key libraries:
- `google-play-scraper`: Play Store scraping
- `pandas`: Data manipulation
- `nltk`: Natural language processing
- `textblob`: Sentiment analysis
- `plotly`: Interactive visualizations
- `jinja2`: HTML templating

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Google Play Store access issues
- Check internet connection
- Try running with a VPN
- Adjust rate limiting in `config.py`

### Sentiment analysis not working
- Ensure NLTK data is downloaded (see Installation)
- Check text preprocessing in `utils/analysis_utils.py`

## License

MIT License - see LICENSE file for details

## Author

Data Science Team

## Support

For issues, questions, or suggestions, please open a GitHub issue.

---

**Last Updated**: July 2026