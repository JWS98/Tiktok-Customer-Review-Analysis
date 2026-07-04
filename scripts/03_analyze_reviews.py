#!/usr/bin/env python
"""
Script 3: Analyze reviews - sentiment, trends, pain points, insights
Performs comprehensive analysis on cleaned review data
"""

import json
import pandas as pd
import sys
from datetime import datetime
from typing import Dict, List
from utils.logger import setup_logger
from utils.analysis_utils import (
    SentimentAnalyzer, KeywordExtractor, identify_pain_points,
    identify_praise_points, calculate_review_stats
)
from config import (
    PROCESSED_DATA_FILE, ANALYSIS_SUMMARY_FILE, PROCESSED_DATA_DIR
)
import os

logger = setup_logger(__name__)

def load_cleaned_reviews() -> pd.DataFrame:
    """
    Load cleaned reviews from CSV
    
    Returns:
        DataFrame with cleaned reviews
    """
    try:
        logger.info(f"Loading cleaned reviews from {PROCESSED_DATA_FILE}")
        df = pd.read_csv(PROCESSED_DATA_FILE)
        logger.info(f"Loaded {len(df)} reviews")
        return df
    except Exception as e:
        logger.error(f"Error loading cleaned reviews: {str(e)}")
        return None

def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform sentiment analysis on reviews
    
    Args:
        df: DataFrame with reviews
    
    Returns:
        DataFrame with sentiment scores added
    """
    logger.info("\nPerforming sentiment analysis...")
    
    sentiments = []
    for idx, row in df.iterrows():
        sentiment = SentimentAnalyzer.analyze(row['content'])
        sentiments.append(sentiment)
        
        if (idx + 1) % 50 == 0:
            logger.info(f"  Analyzed {idx + 1} reviews...")
    
    # Add sentiment columns
    sentiment_df = pd.DataFrame(sentiments)
    df['sentiment_polarity'] = sentiment_df['polarity']
    df['sentiment_subjectivity'] = sentiment_df['subjectivity']
    df['sentiment_label'] = sentiment_df['label']
    
    # Log sentiment distribution
    sentiment_counts = df['sentiment_label'].value_counts()
    logger.info("\nSentiment Distribution:")
    for label, count in sentiment_counts.items():
        percentage = (count / len(df)) * 100
        logger.info(f"  {label}: {count} ({percentage:.1f}%)")
    
    return df

def analyze_trends(df: pd.DataFrame) -> Dict:
    """
    Analyze review trends over time
    
    Args:
        df: DataFrame with reviews
    
    Returns:
        Dictionary with trend analysis
    """
    logger.info("\nAnalyzing trends...")
    
    try:
        df['review_date'] = pd.to_datetime(df['review_date'])
        df['date_only'] = df['review_date'].dt.date
        
        # Daily review count
        daily_counts = df.groupby('date_only').size()
        logger.info("Daily review counts:")
        for date, count in daily_counts.items():
            logger.info(f"  {date}: {count} reviews")
        
        # Daily sentiment
        daily_sentiment = df.groupby('date_only')['sentiment_polarity'].mean()
        logger.info("\nDaily average sentiment (polarity):")
        for date, polarity in daily_sentiment.items():
            logger.info(f"  {date}: {polarity:.3f}")
        
        # Rating trends
        daily_ratings = df.groupby('date_only')['score'].mean()
        
        trends = {
            'daily_review_counts': daily_counts.to_dict(),
            'daily_sentiment': daily_sentiment.to_dict(),
            'daily_ratings': daily_ratings.to_dict()
        }
        
        return trends
    
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        return {}

def extract_insights(df: pd.DataFrame, trends: Dict) -> Dict:
    """
    Extract key insights from analysis
    
    Args:
        df: DataFrame with reviews
        trends: Trend analysis results
    
    Returns:
        Dictionary with insights
    """
    logger.info("\nExtracting key insights...")
    
    try:
        # Pain points
        pain_points = identify_pain_points(
            df.to_dict('records'), top_n=10
        )
        
        # Praise points
        praise_points = identify_praise_points(
            df.to_dict('records'), top_n=10
        )
        
        # Overall stats
        stats = calculate_review_stats(df.to_dict('records'))
        
        # Generate recommendations
        recommendations = generate_recommendations(df, pain_points, praise_points, stats)
        
        insights = {
            'statistics': stats,
            'pain_points': pain_points,
            'praise_points': praise_points,
            'trends': trends,
            'recommendations': recommendations
        }
        
        return insights
    
    except Exception as e:
        logger.error(f"Error extracting insights: {str(e)}")
        return {}

def generate_recommendations(df: pd.DataFrame, pain_points: List[Dict],
                            praise_points: List[Dict], stats: Dict) -> List[str]:
    """
    Generate actionable recommendations based on analysis
    
    Args:
        df: DataFrame with reviews
        pain_points: Identified pain points
        praise_points: Identified praise points
        stats: Review statistics
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Negative sentiment recommendation
    if stats['negative_percentage'] > 30:
        recommendations.append(
            f"⚠️  HIGH NEGATIVE SENTIMENT: {stats['negative_percentage']:.1f}% of reviews are negative. "
            f"Priority should be given to addressing top pain points."
        )
    
    # Pain points recommendation
    if pain_points:
        top_pain = pain_points[0]['keyword']
        recommendations.append(
            f"🔧 TOP ISSUE: '{top_pain}' appears in {pain_points[0]['percentage']:.1f}% of negative reviews. "
            f"Focus on resolving issues related to this."
        )
    
    # Low rating recommendation
    if stats['avg_rating'] < 3.0:
        recommendations.append(
            f"⭐ LOW AVERAGE RATING: Current average rating is {stats['avg_rating']:.1f}/5. "
            f"Significant improvements needed to increase user satisfaction."
        )
    
    # Positive feedback recommendation
    if praise_points:
        top_praise = praise_points[0]['keyword']
        recommendations.append(
            f"✨ STRENGTH TO MAINTAIN: Users frequently praise '{top_praise}'. "
            f"Ensure this feature is prioritized in future updates."
        )
    
    # High positive sentiment
    if stats['positive_percentage'] > 50:
        recommendations.append(
            f"📈 POSITIVE TREND: {stats['positive_percentage']:.1f}% positive reviews indicate strong user satisfaction. "
            f"Maintain quality and capitalize on this momentum."
        )
    
    # Default if no specific issues
    if not recommendations:
        recommendations.append(
            "Continue monitoring review trends and maintain current quality standards."
        )
    
    return recommendations

def save_analysis(df: pd.DataFrame, insights: Dict) -> bool:
    """
    Save analysis results
    
    Args:
        df: DataFrame with analysis
        insights: Extracted insights
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Save enriched CSV
        df_export = df[[
            'review_id', 'user_name', 'content', 'score',
            'sentiment_label', 'sentiment_polarity', 'review_date'
        ]].copy()
        
        csv_file = PROCESSED_DATA_FILE.replace('.csv', '_enriched.csv')
        df_export.to_csv(csv_file, index=False, encoding='utf-8')
        logger.info(f"✓ Saved enriched reviews to {csv_file}")
        
        # Save insights as JSON
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        with open(ANALYSIS_SUMMARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"✓ Saved analysis summary to {ANALYSIS_SUMMARY_FILE}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error saving analysis: {str(e)}")
        return False

def print_analysis_summary(insights: Dict):
    """
    Print analysis summary to console
    
    Args:
        insights: Analysis insights dictionary
    """
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS SUMMARY")
    logger.info("="*80)
    
    stats = insights.get('statistics', {})
    logger.info(f"\nTotal Reviews Analyzed: {stats.get('total_reviews', 0)}")
    logger.info(f"Average Rating: {stats.get('avg_rating', 0):.2f}/5.0")
    logger.info(f"Average Sentiment Polarity: {stats.get('avg_polarity', 0):.3f}")
    
    logger.info(f"\nSentiment Breakdown:")
    logger.info(f"  Positive: {stats.get('positive_count', 0)} ({stats.get('positive_percentage', 0):.1f}%)")
    logger.info(f"  Negative: {stats.get('negative_count', 0)} ({stats.get('negative_percentage', 0):.1f}%)")
    logger.info(f"  Neutral: {stats.get('neutral_count', 0)} ({stats.get('neutral_percentage', 0):.1f}%)")
    
    pain_points = insights.get('pain_points', [])
    if pain_points:
        logger.info(f"\nTop Pain Points:")
        for i, point in enumerate(pain_points[:5], 1):
            logger.info(f"  {i}. {point['keyword']} ({point['frequency']} mentions, {point['percentage']:.1f}% of negative reviews)")
    
    praise_points = insights.get('praise_points', [])
    if praise_points:
        logger.info(f"\nTop Praise Points:")
        for i, point in enumerate(praise_points[:5], 1):
            logger.info(f"  {i}. {point['keyword']} ({point['frequency']} mentions, {point['percentage']:.1f}% of positive reviews)")
    
    recommendations = insights.get('recommendations', [])
    if recommendations:
        logger.info(f"\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec}")

if __name__ == "__main__":
    try:
        logger.info("="*80)
        logger.info("STEP 3: ANALYZING REVIEWS")
        logger.info("="*80)
        
        # Load cleaned reviews
        df = load_cleaned_reviews()
        if df is None or len(df) == 0:
            logger.error("Failed to load cleaned reviews")
            sys.exit(1)
        
        # Sentiment analysis
        df = analyze_sentiment(df)
        
        # Trend analysis
        trends = analyze_trends(df)
        
        # Extract insights
        insights = extract_insights(df, trends)
        
        # Save analysis
        if save_analysis(df, insights):
            # Print summary
            print_analysis_summary(insights)
            
            logger.info("\n✓ Analysis completed successfully!")
            logger.info(f"Ready for next step: generating HTML report")
            sys.exit(0)
        else:
            logger.error("\n✗ Failed to save analysis!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
