#!/usr/bin/env python
"""
Script 4: Generate HTML Report
Creates an interactive HTML report with visualizations and insights
"""

import json
import pandas as pd
import sys
from datetime import datetime
from jinja2 import Template
from utils.logger import setup_logger
from config import (
    ANALYSIS_SUMMARY_FILE, REPORT_FILE, OUTPUT_DIR, APP_NAME,
    PROCESSED_DATA_FILE, CHART_HEIGHT, MAX_ROWS_IN_TABLE
)
import os

logger = setup_logger(__name__)

def load_analysis_data():
    """
    Load analysis data from JSON file
    
    Returns:
        Dictionary with analysis data or None
    """
    try:
        logger.info(f"Loading analysis data from {ANALYSIS_SUMMARY_FILE}")
        with open(ANALYSIS_SUMMARY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error loading analysis data: {str(e)}")
        return None

def load_reviews_for_table():
    """
    Load cleaned reviews for display in HTML table
    
    Returns:
        List of review dictionaries
    """
    try:
        df = pd.read_csv(PROCESSED_DATA_FILE)
        # Get top reviews (sorted by sentiment)
        df_sorted = df.sort_values('score', ascending=False).head(MAX_ROWS_IN_TABLE)
        return df_sorted.to_dict('records')
    except Exception as e:
        logger.warning(f"Could not load reviews for table: {str(e)}")
        return []

def generate_html_report(insights: dict, reviews: list) -> str:
    """
    Generate HTML report using Jinja2 template
    
    Args:
        insights: Analysis insights dictionary
        reviews: List of reviews for table
    
    Returns:
        HTML string
    """
    
    stats = insights.get('statistics', {})
    pain_points = insights.get('pain_points', [])
    praise_points = insights.get('praise_points', [])
    trends = insights.get('trends', {})
    recommendations = insights.get('recommendations', [])
    
    # Prepare data for charts
    daily_counts = trends.get('daily_review_counts', {})
    daily_sentiment = trends.get('daily_sentiment', {})
    daily_ratings = trends.get('daily_ratings', {})
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }} - Review Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .report-date {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .kpi-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            border-top: 4px solid #667eea;
        }
        
        .kpi-card.positive {
            border-top-color: #10b981;
        }
        
        .kpi-card.negative {
            border-top-color: #ef4444;
        }
        
        .kpi-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .kpi-card.positive .kpi-value {
            color: #10b981;
        }
        
        .kpi-card.negative .kpi-value {
            color: #ef4444;
        }
        
        .kpi-label {
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .chart-container {
            margin: 20px 0;
            height: {{ chart_height }}px;
        }
        
        .insights-list {
            list-style: none;
        }
        
        .insights-list li {
            padding: 15px;
            margin: 10px 0;
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }
        
        .pain-point-item, .praise-point-item {
            padding: 12px;
            margin: 8px 0;
            background: #f9f9f9;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .pain-point-item {
            border-left: 4px solid #ef4444;
        }
        
        .praise-point-item {
            border-left: 4px solid #10b981;
        }
        
        .point-keyword {
            font-weight: bold;
            color: #333;
        }
        
        .point-stats {
            color: #666;
            font-size: 0.9em;
        }
        
        .recommendation {
            padding: 15px;
            margin: 12px 0;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid #f59e0b;
            border-radius: 5px;
        }
        
        .recommendation-icon {
            font-size: 1.2em;
            margin-right: 10px;
        }
        
        .review-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .review-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        .review-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .review-table tr:hover {
            background: #f5f5f5;
        }
        
        .sentiment-positive {
            color: #10b981;
            font-weight: bold;
        }
        
        .sentiment-negative {
            color: #ef4444;
            font-weight: bold;
        }
        
        .sentiment-neutral {
            color: #f59e0b;
            font-weight: bold;
        }
        
        .rating {
            font-size: 1.2em;
        }
        
        .star {
            color: #ffc107;
        }
        
        .footer {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
            
            .kpi-container {
                grid-template-columns: 1fr;
            }
            
            .section {
                padding: 15px;
            }
            
            .review-table {
                font-size: 0.9em;
            }
            
            .review-table th, .review-table td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{{ app_name }} Review Analysis</h1>
            <p>Comprehensive Review Analysis Report</p>
            <div class="report-date">Report Generated: {{ report_date }}</div>
        </div>
        
        <!-- KPI Cards -->
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-label">Total Reviews</div>
                <div class="kpi-value">{{ total_reviews }}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Average Rating</div>
                <div class="kpi-value">{{ avg_rating }}/5.0</div>
            </div>
            <div class="kpi-card positive">
                <div class="kpi-label">Positive Reviews</div>
                <div class="kpi-value">{{ positive_percentage }}%</div>
            </div>
            <div class="kpi-card negative">
                <div class="kpi-label">Negative Reviews</div>
                <div class="kpi-value">{{ negative_percentage }}%</div>
            </div>
        </div>
        
        <!-- Sentiment Overview Section -->
        <div class="section">
            <h2 class="section-title">📊 Sentiment Overview</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center;">
                <div>
                    <div style="font-size: 2em; font-weight: bold; color: #10b981;">{{ positive_count }}</div>
                    <div style="color: #666;">Positive ({{ positive_percentage }}%)</div>
                </div>
                <div>
                    <div style="font-size: 2em; font-weight: bold; color: #f59e0b;">{{ neutral_count }}</div>
                    <div style="color: #666;">Neutral ({{ neutral_percentage }}%)</div>
                </div>
                <div>
                    <div style="font-size: 2em; font-weight: bold; color: #ef4444;">{{ negative_count }}</div>
                    <div style="color: #666;">Negative ({{ negative_percentage }}%)</div>
                </div>
            </div>
            <div id="sentiment_chart" class="chart-container"></div>
        </div>
        
        <!-- Pain Points Section -->
        {% if pain_points %}
        <div class="section">
            <h2 class="section-title">🔴 Top Pain Points</h2>
            <p style="color: #666; margin-bottom: 15px;">Most frequently mentioned issues in negative reviews:</p>
            {% for point in pain_points %}
            <div class="pain-point-item">
                <div>
                    <div class="point-keyword">{{ point.keyword }}</div>
                    <div class="point-stats">{{ point.frequency }} mentions • {{ point.percentage }}% of negative reviews</div>
                </div>
            </div>
            {% endfor %}
            <div id="pain_points_chart" class="chart-container"></div>
        </div>
        {% endif %}
        
        <!-- Praise Points Section -->
        {% if praise_points %}
        <div class="section">
            <h2 class="section-title">🟢 Top Praise Points</h2>
            <p style="color: #666; margin-bottom: 15px;">Most frequently mentioned positives in positive reviews:</p>
            {% for point in praise_points %}
            <div class="praise-point-item">
                <div>
                    <div class="point-keyword">{{ point.keyword }}</div>
                    <div class="point-stats">{{ point.frequency }} mentions • {{ point.percentage }}% of positive reviews</div>
                </div>
            </div>
            {% endfor %}
            <div id="praise_points_chart" class="chart-container"></div>
        </div>
        {% endif %}
        
        <!-- Recommendations Section -->
        {% if recommendations %}
        <div class="section">
            <h2 class="section-title">💡 Key Recommendations</h2>
            {% for rec in recommendations %}
            <div class="recommendation">
                {{ rec }}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- Recent Reviews Section -->
        {% if reviews %}
        <div class="section">
            <h2 class="section-title">📝 Recent Reviews</h2>
            <table class="review-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Rating</th>
                        <th>Sentiment</th>
                        <th>Review</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for review in reviews %}
                    <tr>
                        <td>{{ review.user_name[:20] }}</td>
                        <td class="rating">
                            {% for i in range(review.score) %}
                            <span class="star">★</span>
                            {% endfor %}
                        </td>
                        <td>
                            {% if review.sentiment_label == 'Positive' %}
                            <span class="sentiment-positive">{{ review.sentiment_label }}</span>
                            {% elif review.sentiment_label == 'Negative' %}
                            <span class="sentiment-negative">{{ review.sentiment_label }}</span>
                            {% else %}
                            <span class="sentiment-neutral">{{ review.sentiment_label }}</span>
                            {% endif %}
                        </td>
                        <td>{{ review.content[:100] }}...</td>
                        <td>{{ review.review_date[:10] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <!-- Footer -->
        <div class="footer">
            <p>🤖 Generated by TikTok Review Analysis System</p>
            <p>Data Analysis Dashboard • {{ report_date }}</p>
        </div>
    </div>
    
    <!-- Chart Scripts -->
    <script>
        // Sentiment Distribution Chart
        var sentimentData = [{
            labels: ['Positive', 'Neutral', 'Negative'],
            values: [{{ positive_count }}, {{ neutral_count }}, {{ negative_count }}],
            type: 'pie',
            marker: {colors: ['#10b981', '#f59e0b', '#ef4444']}
        }];
        Plotly.newPlot('sentiment_chart', sentimentData, {title: '', margin: {t: 20}});
        
        // Pain Points Chart
        {% if pain_points %}
        var painPointsLabels = [{% for point in pain_points %}'{{ point.keyword }}'{{ ", " if not loop.last }}{% endfor %}];
        var painPointsValues = [{% for point in pain_points %}{{ point.frequency }}{{ ", " if not loop.last }}{% endfor %}];
        var painPointsData = [{
            y: painPointsLabels,
            x: painPointsValues,
            type: 'bar',
            orientation: 'h',
            marker: {color: '#ef4444'}
        }];
        Plotly.newPlot('pain_points_chart', painPointsData, {title: '', xaxis: {title: 'Frequency'}, margin: {l: 150}});
        {% endif %}
        
        // Praise Points Chart
        {% if praise_points %}
        var praisePointsLabels = [{% for point in praise_points %}'{{ point.keyword }}'{{ ", " if not loop.last }}{% endfor %}];
        var praisePointsValues = [{% for point in praise_points %}{{ point.frequency }}{{ ", " if not loop.last }}{% endfor %}];
        var praisePointsData = [{
            y: praisePointsLabels,
            x: praisePointsValues,
            type: 'bar',
            orientation: 'h',
            marker: {color: '#10b981'}
        }];
        Plotly.newPlot('praise_points_chart', praisePointsData, {title: '', xaxis: {title: 'Frequency'}, margin: {l: 150}});
        {% endif %}
    </script>
</body>
</html>
    """
    
    template = Template(html_template)
    html_content = template.render(
        app_name=APP_NAME,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_reviews=stats.get('total_reviews', 0),
        avg_rating=stats.get('avg_rating', 0),
        positive_count=stats.get('positive_count', 0),
        positive_percentage=stats.get('positive_percentage', 0),
        negative_count=stats.get('negative_count', 0),
        negative_percentage=stats.get('negative_percentage', 0),
        neutral_count=stats.get('neutral_count', 0),
        neutral_percentage=stats.get('neutral_percentage', 0),
        pain_points=pain_points[:10],
        praise_points=praise_points[:10],
        recommendations=recommendations,
        reviews=reviews,
        chart_height=CHART_HEIGHT
    )
    
    return html_content

def save_report(html_content: str) -> bool:
    """
    Save HTML report to file
    
    Args:
        html_content: HTML string
    
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✓ Report saved to {REPORT_FILE}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving report: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        logger.info("="*80)
        logger.info("STEP 4: GENERATING HTML REPORT")
        logger.info("="*80)
        
        # Load analysis data
        insights = load_analysis_data()
        if not insights:
            logger.error("Failed to load analysis data")
            sys.exit(1)
        
        # Load reviews for table
        reviews = load_reviews_for_table()
        logger.info(f"Loaded {len(reviews)} reviews for table")
        
        # Generate HTML report
        logger.info("Generating HTML report...")
        html_content = generate_html_report(insights, reviews)
        
        # Save report
        if save_report(html_content):
            logger.info("\n" + "="*80)
            logger.info("✓ REPORT GENERATION COMPLETED SUCCESSFULLY!")
            logger.info("="*80)
            logger.info(f"\nReport Location: {REPORT_FILE}")
            logger.info(f"\nOpen the report in your browser to view the analysis.")
            sys.exit(0)
        else:
            logger.error("\n✗ Failed to save report!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\nReport generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
