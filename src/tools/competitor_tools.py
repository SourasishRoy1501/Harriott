"""
LangChain tools for competitor analysis
"""
from langchain.tools import tool
from datetime import date
from typing import Dict, Any

from src.database.queries import (
    get_competitors,
    analyze_price_gap,
    compare_amenities,
    get_booking_trends,
    get_property_by_id
)
from src.utils.date_helpers import get_date_range


@tool
def analyze_competitor_pricing(property_id: str, end_date: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyze pricing gap between property and competitors.
    
    Args:
        property_id: Property identifier
        end_date: End date in YYYY-MM-DD format
        lookback_days: Number of days to analyze
    
    Returns:
        Dictionary with pricing comparison and gap analysis
    """
    end_date_obj = date.fromisoformat(end_date)
    start_date, _ = get_date_range(end_date_obj, lookback_days)
    
    # Get property's average rate
    booking_trends = get_booking_trends(property_id, start_date, end_date_obj)
    if not booking_trends:
        return {"error": "No booking data available for property"}
    
    property_avg_rate = sum(t.avg_daily_rate for t in booking_trends) / len(booking_trends)
    
    # Get competitors
    competitors = get_competitors(property_id)
    if not competitors:
        return {"error": "No competitors defined for this property"}
    
    # Analyze price gap
    price_analysis = analyze_price_gap(
        property_id, 
        competitors, 
        property_avg_rate, 
        start_date, 
        end_date_obj
    )
    
    if "error" in price_analysis:
        return price_analysis
    
    # Add interpretation
    gap_pct = price_analysis["price_gap_percentage"]
    if gap_pct > 15:
        interpretation = "Property is significantly more expensive - may be losing price-sensitive customers"
    elif gap_pct > 5:
        interpretation = "Property is slightly premium - positioning may need adjustment"
    elif gap_pct < -10:
        interpretation = "Property is significantly cheaper - may be perceived as lower quality"
    else:
        interpretation = "Pricing is competitive with nearby alternatives"
    
    price_analysis["interpretation"] = interpretation
    
    return price_analysis


@tool
def compare_property_amenities(property_id: str) -> Dict[str, Any]:
    """
    Compare property amenities with competitors to identify gaps.
    
    Args:
        property_id: Property identifier
    
    Returns:
        Dictionary with amenity comparison and gaps
    """
    competitors = get_competitors(property_id)
    if not competitors:
        return {"error": "No competitors defined"}
    
    amenity_comparison = compare_amenities(property_id, competitors)
    
    if "error" in amenity_comparison:
        return amenity_comparison
    
    # Add impact assessment
    gaps = amenity_comparison.get("gaps", [])
    critical_amenities = ["wifi", "parking", "gym", "breakfast"]
    
    critical_gaps = [
        gap for gap in gaps 
        if any(critical in gap["amenity"].lower() for critical in critical_amenities)
    ]
    
    amenity_comparison["critical_gaps"] = critical_gaps
    amenity_comparison["critical_gap_count"] = len(critical_gaps)
    
    if critical_gaps:
        amenity_comparison["impact_assessment"] = "HIGH - Missing amenities that most competitors offer"
    elif gaps:
        amenity_comparison["impact_assessment"] = "MEDIUM - Some amenity gaps exist"
    else:
        amenity_comparison["impact_assessment"] = "LOW - Amenities are competitive"
    
    return amenity_comparison


@tool
def get_competitor_context(property_id: str) -> Dict[str, Any]:
    """
    Get overall competitive landscape context.
    
    Args:
        property_id: Property identifier
    
    Returns:
        Dictionary with competitive context
    """
    property_info = get_property_by_id(property_id)
    if not property_info:
        return {"error": "Property not found"}
    
    competitors = get_competitors(property_id)
    if not competitors:
        return {"error": "No competitors defined"}
    
    # Categorize by distance
    nearby = [c for c in competitors if c.distance_km <= 1]
    close = [c for c in competitors if 1 < c.distance_km <= 3]
    distant = [c for c in competitors if c.distance_km > 3]
    
    # Categorize by category
    same_category = [c for c in competitors if c.category == property_info.category]
    premium = [c for c in competitors if c.category == "premium" and property_info.category != "premium"]
    budget = [c for c in competitors if c.category == "budget" and property_info.category != "budget"]
    
    return {
        "property_category": property_info.category,
        "total_competitors": len(competitors),
        "by_distance": {
            "nearby_1km": len(nearby),
            "close_1_3km": len(close),
            "distant_3km_plus": len(distant)
        },
        "by_category": {
            "same_category": len(same_category),
            "premium_competitors": len(premium),
            "budget_competitors": len(budget)
        },
        "competitive_pressure": _assess_competitive_pressure(nearby, same_category),
        "top_competitors": [
            {"name": c.name, "distance_km": c.distance_km, "category": c.category}
            for c in competitors[:5]
        ]
    }


def _assess_competitive_pressure(nearby, same_category) -> str:
    """Helper to assess competitive pressure"""
    if len(nearby) >= 3 and len(same_category) >= 2:
        return "HIGH - Multiple nearby competitors in same category"
    elif len(nearby) >= 2 or len(same_category) >= 3:
        return "MEDIUM - Moderate competition in area"
    else:
        return "LOW - Limited direct competition"


# Export all tools
competitor_tools = [
    analyze_competitor_pricing,
    compare_property_amenities,
    get_competitor_context
]
