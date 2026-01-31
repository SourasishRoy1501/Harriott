"""
LangChain tools for weather data analysis
"""
from langchain.tools import tool
from datetime import date
from typing import Dict, Any

from src.database.queries import (
    get_weather_data,
    detect_weather_events,
    get_property_by_id
)
from src.utils.date_helpers import get_date_range


@tool
def analyze_weather_impact(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyze weather conditions and their potential impact on bookings.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with weather analysis and travel impact assessment
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    # Get property to find city
    property_info = get_property_by_id(property_id)
    if not property_info:
        return {"error": "Property not found"}
    
    weather_data = get_weather_data(property_info.city, start_date, end_date_obj)
    
    if not weather_data:
        return {"error": "No weather data available"}
    
    # Detect significant events
    events = detect_weather_events(weather_data)
    
    # Calculate statistics
    avg_temp = sum(w.temperature for w in weather_data) / len(weather_data)
    total_rainfall = sum(w.rainfall_mm for w in weather_data)
    rainy_days = len([w for w in weather_data if w.rainfall_mm > 10])
    
    return {
        "city": property_info.city,
        "period": f"{start_date} to {end_date}",
        "avg_temperature": round(avg_temp, 1),
        "total_rainfall_mm": round(total_rainfall, 1),
        "rainy_days": rainy_days,
        "rainy_day_percentage": round(rainy_days / len(weather_data) * 100, 2),
        "significant_events": events["events"],
        "travel_impact_assessment": _assess_travel_impact(weather_data, events)
    }


@tool
def detect_extreme_weather_events(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Detect extreme weather events that could deter travel.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with extreme weather events
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    property_info = get_property_by_id(property_id)
    if not property_info:
        return {"error": "Property not found"}
    
    weather_data = get_weather_data(property_info.city, start_date, end_date_obj)
    
    if not weather_data:
        return {"error": "No weather data available"}
    
    extreme_events = []
    
    # Heavy rainfall (> 50mm)
    heavy_rain = [w for w in weather_data if w.rainfall_mm > 50]
    if heavy_rain:
        extreme_events.append({
            "type": "heavy_rainfall",
            "severity": "high",
            "days_affected": len(heavy_rain),
            "max_rainfall": max(w.rainfall_mm for w in heavy_rain),
            "dates": [str(w.date) for w in heavy_rain[:5]],
            "impact": "Likely deterred leisure and business travel"
        })
    
    # Moderate rainfall (20-50mm)
    moderate_rain = [w for w in weather_data if 20 < w.rainfall_mm <= 50]
    if moderate_rain:
        extreme_events.append({
            "type": "moderate_rainfall",
            "severity": "medium",
            "days_affected": len(moderate_rain),
            "impact": "May have reduced outdoor activities and day trips"
        })
    
    # Temperature extremes
    avg_temp = sum(w.temperature for w in weather_data) / len(weather_data)
    hot_days = [w for w in weather_data if w.temperature > avg_temp + 8]
    cold_days = [w for w in weather_data if w.temperature < avg_temp - 8]
    
    if hot_days:
        extreme_events.append({
            "type": "extreme_heat",
            "severity": "medium",
            "days_affected": len(hot_days),
            "max_temp": max(w.temperature for w in hot_days),
            "impact": "May have reduced outdoor tourism activities"
        })
    
    if cold_days:
        extreme_events.append({
            "type": "extreme_cold",
            "severity": "medium",
            "days_affected": len(cold_days),
            "min_temp": min(w.temperature for w in cold_days),
            "impact": "May have deterred leisure travelers"
        })
    
    return {
        "extreme_events_found": len(extreme_events),
        "events": extreme_events,
        "overall_assessment": _get_weather_severity(extreme_events)
    }


def _assess_travel_impact(weather_data, events_dict) -> str:
    """Helper to assess travel impact from weather"""
    events = events_dict.get("events", [])
    
    if not events:
        return "No significant weather impact detected"
    
    high_impact_events = [e for e in events if e.get("impact") == "high"]
    
    if high_impact_events:
        return "HIGH - Extreme weather likely deterred significant travel"
    elif len(events) > 1:
        return "MEDIUM - Multiple weather events may have reduced bookings"
    else:
        return "LOW - Minor weather impact, unlikely to be primary cause"


def _get_weather_severity(events) -> str:
    """Helper to determine overall weather severity"""
    if not events:
        return "Normal weather conditions"
    
    high_severity = sum(1 for e in events if e.get("severity") == "high")
    
    if high_severity >= 2:
        return "Severe weather period - strong deterrent to travel"
    elif high_severity == 1:
        return "Significant weather disruption occurred"
    else:
        return "Moderate weather variations observed"


# Export all tools
weather_tools = [
    analyze_weather_impact,
    detect_extreme_weather_events
]
