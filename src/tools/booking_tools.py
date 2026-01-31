"""
LangChain tools for booking trends and occupancy data
"""
from langchain.tools import tool
from datetime import date, timedelta
from typing import Dict, Any

from src.database.queries import (
    get_booking_trends,
    calculate_occupancy_drop
)
from src.utils.date_helpers import get_date_range


@tool
def get_occupancy_trends(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Get occupancy trends for a property over a specified period.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to look back (default: 30)
    
    Returns:
        Dictionary containing occupancy trends, average rates, and statistics
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    trends = get_booking_trends(property_id, start_date, end_date_obj)
    
    if not trends:
        return {"error": "No booking data available"}
    
    # Calculate statistics
    avg_occupancy = sum(t.occupancy_percentage for t in trends) / len(trends)
    avg_rate = sum(t.avg_daily_rate for t in trends) / len(trends)
    total_bookings = sum(t.bookings for t in trends)
    
    # Find min and max occupancy
    min_occupancy = min(t.occupancy_percentage for t in trends)
    max_occupancy = max(t.occupancy_percentage for t in trends)
    
    return {
        "period": f"{start_date} to {end_date}",
        "total_days": len(trends),
        "avg_occupancy_percentage": round(avg_occupancy, 2),
        "avg_daily_rate": round(avg_rate, 2),
        "total_bookings": total_bookings,
        "min_occupancy": round(min_occupancy, 2),
        "max_occupancy": round(max_occupancy, 2),
        "volatility": round(max_occupancy - min_occupancy, 2),
        "daily_trends": [
            {
                "date": str(t.date),
                "occupancy": t.occupancy_percentage,
                "bookings": t.bookings,
                "rate": t.avg_daily_rate
            }
            for t in trends[-10:]  # Last 10 days for context
        ]
    }


@tool
def analyze_occupancy_drop(property_id: str, current_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyze occupancy drop by comparing two periods.
    
    Args:
        property_id: Property identifier
        current_date: Analysis date in YYYY-MM-DD format
        lookback_days: Number of days to analyze (default: 30)
    
    Returns:
        Dictionary with drop analysis including percentage change and trend
    """
    current_date_obj = date.fromisoformat(current_date)
    drop_metrics = calculate_occupancy_drop(property_id, current_date_obj, lookback_days)
    
    return drop_metrics


@tool
def check_weekday_weekend_pattern(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyze weekday vs weekend occupancy patterns.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary comparing weekday vs weekend occupancy
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    trends = get_booking_trends(property_id, start_date, end_date_obj)
    
    if not trends:
        return {"error": "No booking data available"}
    
    weekday_occupancy = []
    weekend_occupancy = []
    
    for trend in trends:
        if trend.date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            weekend_occupancy.append(trend.occupancy_percentage)
        else:
            weekday_occupancy.append(trend.occupancy_percentage)
    
    avg_weekday = sum(weekday_occupancy) / len(weekday_occupancy) if weekday_occupancy else 0
    avg_weekend = sum(weekend_occupancy) / len(weekend_occupancy) if weekend_occupancy else 0
    
    return {
        "avg_weekday_occupancy": round(avg_weekday, 2),
        "avg_weekend_occupancy": round(avg_weekend, 2),
        "difference": round(avg_weekend - avg_weekday, 2),
        "weekday_dominant": avg_weekday > avg_weekend,
        "pattern": "weekday-focused" if avg_weekday > avg_weekend else "weekend-focused"
    }


# Export all tools
booking_tools = [
    get_occupancy_trends,
    analyze_occupancy_drop,
    check_weekday_weekend_pattern
]
