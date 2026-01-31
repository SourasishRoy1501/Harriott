"""
LangChain tools for review analysis and sentiment
"""
from langchain.tools import tool
from datetime import date
from typing import Dict, Any, List

from src.database.queries import get_reviews
from src.utils.nlp_helpers import (
    extract_themes_from_reviews,
    analyze_sentiment_trend,
    filter_negative_reviews
)
from src.utils.date_helpers import get_date_range


@tool
def analyze_review_themes(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Extract and analyze dominant themes from guest reviews.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with top themes, sentiment scores, and sample quotes
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    reviews = get_reviews(property_id, start_date, end_date_obj)
    
    if not reviews:
        return {"error": "No reviews available for analysis"}
    
    themes = extract_themes_from_reviews(reviews)
    
    return {
        "total_reviews": len(reviews),
        "analysis_period": f"{start_date} to {end_date}",
        "top_themes": [
            {
                "theme": theme.theme,
                "sentiment_score": theme.sentiment_score,
                "sentiment": "positive" if theme.sentiment_score > 0.1 else "negative" if theme.sentiment_score < -0.1 else "neutral",
                "mentions": theme.mention_count,
                "sample_quotes": theme.sample_quotes
            }
            for theme in themes[:5]  # Top 5 themes
        ]
    }


@tool
def get_negative_review_insights(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyze negative reviews (rating <= 3) to identify problems.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with negative review analysis and common complaints
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    all_reviews = get_reviews(property_id, start_date, end_date_obj)
    negative_reviews = filter_negative_reviews(all_reviews)
    
    if not negative_reviews:
        return {
            "total_reviews": len(all_reviews),
            "negative_reviews": 0,
            "message": "No negative reviews found"
        }
    
    themes = extract_themes_from_reviews(negative_reviews)
    
    return {
        "total_reviews": len(all_reviews),
        "negative_reviews": len(negative_reviews),
        "negative_percentage": round(len(negative_reviews) / len(all_reviews) * 100, 2),
        "common_complaints": [
            {
                "theme": theme.theme,
                "mentions": theme.mention_count,
                "severity": "high" if theme.sentiment_score < -0.3 else "medium",
                "examples": theme.sample_quotes[:2]
            }
            for theme in themes[:3]  # Top 3 complaints
        ]
    }


@tool
def analyze_review_sentiment_trend(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyze sentiment trend over time to detect deterioration or improvement.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with sentiment trend analysis
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    reviews = get_reviews(property_id, start_date, end_date_obj)
    
    if not reviews:
        return {"error": "No reviews available"}
    
    trend_data = analyze_sentiment_trend(reviews)
    
    return {
        "trend": trend_data["trend"],
        "first_period": {
            "sentiment": trend_data["first_period_sentiment"],
            "avg_rating": trend_data["first_period_rating"]
        },
        "second_period": {
            "sentiment": trend_data["second_period_sentiment"],
            "avg_rating": trend_data["second_period_rating"]
        },
        "changes": {
            "sentiment_change": trend_data["sentiment_change"],
            "rating_change": trend_data["rating_change"]
        },
        "interpretation": (
            "Reviews are getting more negative over time" if trend_data["trend"] == "declining"
            else "Reviews are improving over time"
        )
    }


@tool
def get_rating_distribution(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Get distribution of ratings to understand review patterns.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with rating distribution
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    reviews = get_reviews(property_id, start_date, end_date_obj)
    
    if not reviews:
        return {"error": "No reviews available"}
    
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
    
    total = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / total
    
    return {
        "total_reviews": total,
        "avg_rating": round(avg_rating, 2),
        "distribution": {
            str(rating): {
                "count": count,
                "percentage": round(count / total * 100, 2)
            }
            for rating, count in rating_counts.items()
        },
        "polarization": (
            "high" if (rating_counts[5] + rating_counts[1]) / total > 0.6
            else "low"
        )
    }


# Export all tools
review_tools = [
    analyze_review_themes,
    get_negative_review_insights,
    analyze_review_sentiment_trend,
    get_rating_distribution
]
