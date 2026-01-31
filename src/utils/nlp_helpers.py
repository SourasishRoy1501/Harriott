"""
NLP utilities for review analysis and sentiment extraction
"""
from typing import List, Dict, Any, Tuple
from collections import Counter
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger

from src.models.schemas import Review, ReviewTheme


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of text using TextBlob
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment score between -1 (negative) and 1 (positive)
    """
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        return 0.0


def categorize_sentiment(score: float) -> str:
    """
    Categorize sentiment score into label
    
    Args:
        score: Sentiment score
        
    Returns:
        Category: positive, neutral, or negative
    """
    if score > 0.1:
        return "positive"
    elif score < -0.1:
        return "negative"
    else:
        return "neutral"


# ============================================================================
# THEME EXTRACTION
# ============================================================================

# Common hospitality themes and keywords
THEME_KEYWORDS = {
    "cleanliness": ["clean", "dirty", "hygiene", "sanitize", "tidy", "mess", "spotless"],
    "wifi": ["wifi", "wi-fi", "internet", "connection", "bandwidth", "network"],
    "service": ["staff", "service", "helpful", "friendly", "rude", "attentive", "responsive"],
    "noise": ["noise", "noisy", "loud", "quiet", "peaceful", "disturbance", "sleep"],
    "location": ["location", "convenient", "accessible", "nearby", "distance", "central"],
    "amenities": ["amenities", "facilities", "pool", "gym", "spa", "restaurant"],
    "room": ["room", "bed", "comfortable", "spacious", "cramped", "cozy"],
    "value": ["value", "price", "expensive", "cheap", "worth", "money", "affordable"],
    "food": ["food", "breakfast", "restaurant", "meal", "dining", "menu"],
    "maintenance": ["maintenance", "repair", "broken", "working", "fix", "condition"]
}


def extract_themes_from_reviews(reviews: List[Review]) -> List[ReviewTheme]:
    """
    Extract dominant themes from reviews with sentiment
    
    Args:
        reviews: List of Review models
        
    Returns:
        List of ReviewTheme models with sentiment and frequency
    """
    if not reviews:
        return []
    
    theme_mentions: Dict[str, List[Tuple[str, float]]] = {theme: [] for theme in THEME_KEYWORDS}
    
    for review in reviews:
        text_lower = review.review_text.lower()
        sentiment = analyze_sentiment(review.review_text)
        
        # Check for theme keywords
        for theme, keywords in THEME_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    theme_mentions[theme].append((review.review_text, sentiment))
                    break  # Count each review only once per theme
    
    # Build ReviewTheme objects
    themes = []
    for theme, mentions in theme_mentions.items():
        if mentions:
            avg_sentiment = sum(s for _, s in mentions) / len(mentions)
            sample_quotes = [
                text[:100] + "..." if len(text) > 100 else text
                for text, _ in mentions[:3]
            ]
            
            themes.append(ReviewTheme(
                theme=theme,
                sentiment_score=round(avg_sentiment, 2),
                mention_count=len(mentions),
                sample_quotes=sample_quotes
            ))
    
    # Sort by mention count (most frequent first)
    themes.sort(key=lambda x: x.mention_count, reverse=True)
    
    return themes


def extract_keywords_tfidf(reviews: List[Review], top_n: int = 20) -> List[Tuple[str, float]]:
    """
    Extract top keywords using TF-IDF
    
    Args:
        reviews: List of reviews
        top_n: Number of top keywords to return
        
    Returns:
        List of (keyword, score) tuples
    """
    if not reviews:
        return []
    
    try:
        texts = [review.review_text for review in reviews]
        
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # Sum TF-IDF scores across all documents
        scores = tfidf_matrix.sum(axis=0).A1
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return keyword_scores[:top_n]
    except Exception as e:
        logger.error(f"TF-IDF extraction failed: {e}")
        return []


# ============================================================================
# REVIEW FILTERING
# ============================================================================

def filter_negative_reviews(reviews: List[Review], threshold: int = 3) -> List[Review]:
    """
    Filter reviews with rating below threshold
    
    Args:
        reviews: List of reviews
        threshold: Rating threshold (inclusive)
        
    Returns:
        List of negative reviews
    """
    return [r for r in reviews if r.rating <= threshold]


def filter_recent_reviews(reviews: List[Review], days: int = 30) -> List[Review]:
    """
    Filter reviews from last N days
    
    Args:
        reviews: List of reviews
        days: Number of days to look back
        
    Returns:
        List of recent reviews
    """
    from datetime import datetime, timedelta
    cutoff_date = datetime.now().date() - timedelta(days=days)
    return [r for r in reviews if r.review_date >= cutoff_date]


# ============================================================================
# SENTIMENT TREND ANALYSIS
# ============================================================================

def analyze_sentiment_trend(reviews: List[Review]) -> Dict[str, Any]:
    """
    Analyze sentiment trend over time
    
    Args:
        reviews: List of reviews sorted by date
        
    Returns:
        Dictionary with trend analysis
    """
    if not reviews:
        return {"trend": "insufficient_data"}
    
    # Sort by date
    sorted_reviews = sorted(reviews, key=lambda x: x.review_date)
    
    # Split into periods
    mid_point = len(sorted_reviews) // 2
    first_half = sorted_reviews[:mid_point]
    second_half = sorted_reviews[mid_point:]
    
    # Calculate average sentiment
    first_sentiment = sum(analyze_sentiment(r.review_text) for r in first_half) / len(first_half)
    second_sentiment = sum(analyze_sentiment(r.review_text) for r in second_half) / len(second_half)
    
    # Calculate average rating
    first_rating = sum(r.rating for r in first_half) / len(first_half)
    second_rating = sum(r.rating for r in second_half) / len(second_half)
    
    trend = "improving" if second_sentiment > first_sentiment else "declining"
    
    return {
        "trend": trend,
        "first_period_sentiment": round(first_sentiment, 2),
        "second_period_sentiment": round(second_sentiment, 2),
        "first_period_rating": round(first_rating, 2),
        "second_period_rating": round(second_rating, 2),
        "sentiment_change": round(second_sentiment - first_sentiment, 2),
        "rating_change": round(second_rating - first_rating, 2)
    }


# ============================================================================
# TEXT CLEANING
# ============================================================================

def clean_review_text(text: str) -> str:
    """
    Clean and normalize review text
    
    Args:
        text: Raw review text
        
    Returns:
        Cleaned text
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove special characters but keep punctuation for sentiment
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()
