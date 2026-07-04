# Quick Start Guide

## Installation & Setup (5 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/JWS98/Tiktok-Customer-Review-Analysis.git
cd Tiktok-Customer-Review-Analysis
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data (First time only)
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

---

## Running the Analysis

### Quick Run (Recommended)
```bash
python main.py
```

This runs all 4 steps automatically:
1. ✅ Scrapes reviews from Google Play Store
2. ✅ Cleans and validates the data
3. ✅ Performs sentiment and trend analysis
4. ✅ Generates an interactive HTML report

**Expected time**: 5-15 minutes (depends on network speed and number of reviews)

### Individual Steps

If you prefer to run steps individually:

```bash
# Step 1: Scrape reviews
python scripts/01_scrape_reviews.py

# Step 2: Clean data
python scripts/02_clean_data.py

# Step 3: Analyze reviews
python scripts/03_analyze_reviews.py

# Step 4: Generate report
python scripts/04_generate_report.py
```

---

## Viewing Results

### 📊 Main Report
After running the pipeline, open the report in your browser:
```
output/review.html
```

### 📁 Generated Files

- **`data/raw/`** - Raw scraped reviews (JSON format)
- **`data/processed/reviews_clean.csv`** - Cleaned reviews (CSV)
- **`data/processed/reviews_enriched.csv`** - Cleaned reviews with sentiment scores
- **`data/processed/analysis_summary.json`** - Detailed analysis in JSON
- **`output/review.html`** - Interactive HTML dashboard
- **`logs/app.log`** - Execution logs for debugging

---

## Configuration

Edit `config.py` to customize:

### Scraping Parameters
```python
REVIEWS_TO_SCRAPE = 500        # Number of reviews to fetch
DAYS_TO_ANALYZE = 10           # Look back period in days
SORT_BY = "newest"             # Options: newest, rating, most_helpful
```

### Analysis Parameters
```python
SENTIMENT_THRESHOLD_POSITIVE = 0.5    # Threshold for positive sentiment
SENTIMENT_THRESHOLD_NEGATIVE = -0.5   # Threshold for negative sentiment
MIN_KEYWORD_FREQUENCY = 2             # Minimum occurrences for a keyword
MAX_KEYWORDS = 10                     # Top N keywords to extract
```

### Report Settings
```python
REPORT_THEME = "light"                # light or dark
MAX_ROWS_IN_TABLE = 50                # Reviews to show in table
CHART_HEIGHT = 400                    # Chart height in pixels
```

---

## Features

### 📊 Data Analysis
- **Sentiment Analysis**: Classify reviews as Positive, Negative, or Neutral
- **Pain Point Extraction**: Identify most common complaints
- **Praise Point Extraction**: Identify most common praise
- **Trend Analysis**: Track sentiment and rating trends over time
- **Statistical Analysis**: Calculate averages, distributions, correlations

### 📈 Visualizations
- Sentiment distribution pie chart
- Pain points bar chart
- Praise points bar chart
- Daily review volume trends
- Interactive Plotly charts

### 📋 Report Contents
- Executive summary with key metrics
- KPI cards (total reviews, avg rating, sentiment breakdown)
- Detailed pain points analysis
- Praise points identification
- Actionable recommendations
- Sample review table
- All data exported to CSV/JSON

---

## Troubleshooting

### "Module not found" Error
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Google Play Store" Connection Issues
- Check your internet connection
- Try using a VPN
- Check `logs/app.log` for details
- Increase `RATE_LIMIT_DELAY` in `config.py`

### NLTK Data Not Found
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

### Memory Issues with Large Datasets
- Reduce `REVIEWS_TO_SCRAPE` in `config.py`
- Reduce `DAYS_TO_ANALYZE` to get fewer reviews

### Report Not Generating
- Check `logs/app.log` for error messages
- Ensure `data/processed/analysis_summary.json` exists
- Try running `scripts/04_generate_report.py` directly

---

## Advanced Usage

### Custom Data Analysis
Load the enriched CSV for additional analysis:
```python
import pandas as pd

df = pd.read_csv('data/processed/reviews_enriched.csv')
print(df.describe())
print(df['sentiment_label'].value_counts())
```

### Accessing Raw Data
```python
import json

with open('data/processed/analysis_summary.json', 'r') as f:
    insights = json.load(f)

print(insights['statistics'])
print(insights['pain_points'])
print(insights['recommendations'])
```

---

## Performance Notes

- **Scraping**: 5-10 minutes (depends on network)
- **Cleaning**: 30 seconds - 2 minutes
- **Analysis**: 1-3 minutes (depends on number of reviews)
- **Report Generation**: 10-30 seconds

**Total expected time**: 10-20 minutes for 500 reviews

---

## Next Steps

1. ✅ Run the pipeline: `python main.py`
2. ✅ Open `output/review.html` in your browser
3. ✅ Review the insights and recommendations
4. ✅ Export data for further analysis if needed
5. ✅ Schedule regular runs to track trends over time

---

## Support & Feedback

For issues, questions, or feature requests, please open a GitHub issue.

**Happy analyzing! 🚀**
