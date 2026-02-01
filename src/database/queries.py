"""
Database queries for SOA data retrieval
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger

from src.database.supabase_client import get_supabase_client
from src.models.schemas import (
    Property, BookingTrend, Review, WeatherData, 
    Competitor, CompetitorPricing
)


# ============================================================================
# PROPERTY QUERIES
# ============================================================================

def get_property_by_id(property_id: str) -> Optional[Property]:
    """
    Get property details by ID
    
    Args:
        property_id: Property identifier
        
    Returns:
        Property model or None if not found
    """
    try:
        client = get_supabase_client()
        response = client.table("properties").select("*").eq("id", property_id).execute()
        
        if response.data and len(response.data) > 0:
            return Property(**response.data[0])
        
        logger.warning(f"Property {property_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error fetching property {property_id}: {e}")
        return None


def get_all_properties() -> List[Property]:
    """
    Get all properties in portfolio
    
    Returns:
        List of Property models
    """
    try:
        client = get_supabase_client()
        response = client.table("properties").select("*").execute()
        
        return [Property(**item) for item in response.data]
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        return []


# ============================================================================
# BOOKING TRENDS QUERIES
# ============================================================================

def get_booking_trends(
    property_id: str,
    start_date: date,
    end_date: date
) -> List[BookingTrend]:
    """
    Get booking trends for a property within date range
    
    Args:
        property_id: Property identifier
        start_date: Start of analysis period
        end_date: End of analysis period
        
    Returns:
        List of BookingTrend models sorted by date
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("booking_trends")
            .select("*")
            .eq("property_id", property_id)
            .gte("date", start_date.isoformat())
            .lte("date", end_date.isoformat())
            .order("date")
            .execute()
        )
        
        return [BookingTrend(**item) for item in response.data]
    except Exception as e:
        logger.error(f"Error fetching booking trends for {property_id}: {e}")
        return []


def calculate_occupancy_drop(
    property_id: str,
    current_date: date,
    lookback_days: int = 30
) -> Dict[str, Any]:
    """
    Calculate occupancy drop metrics
    
    Args:
        property_id: Property identifier
        current_date: Analysis date
        lookback_days: Days to look back
        
    Returns:
        Dictionary with drop metrics
    """
    try:
        end_date = current_date
        start_date = current_date - timedelta(days=lookback_days)
        
        trends = get_booking_trends(property_id, start_date, end_date)
        
        if not trends:
            return {"error": "No booking data available"}
        
        # Split into two periods for comparison
        mid_point = len(trends) // 2
        first_half = trends[:mid_point]
        second_half = trends[mid_point:]
        
        avg_first = sum(t.occupancy_percentage for t in first_half) / len(first_half) if first_half else 0
        avg_second = sum(t.occupancy_percentage for t in second_half) / len(second_half) if second_half else 0
        
        drop_percentage = avg_first - avg_second
        drop_ratio = (drop_percentage / avg_first * 100) if avg_first > 0 else 0
        
        return {
            "first_period_avg": round(avg_first, 2),
            "second_period_avg": round(avg_second, 2),
            "drop_percentage": round(drop_percentage, 2),
            "drop_ratio": round(drop_ratio, 2),
            "trend": "declining" if drop_percentage > 0 else "stable"
        }
    except Exception as e:
        logger.error(f"Error calculating occupancy drop: {e}")
        return {"error": str(e)}


# ============================================================================
# REVIEWS QUERIES
# ============================================================================

def get_reviews(
    property_id: str,
    start_date: date,
    end_date: date,
    min_rating: Optional[int] = None
) -> List[Review]:
    """
    Get reviews for a property within date range
    
    Args:
        property_id: Property identifier
        start_date: Start date
        end_date: End date
        min_rating: Optional minimum rating filter
        
    Returns:
        List of Review models
    """
    try:
        client = get_supabase_client()
        query = (
            client.table("reviews")
            .select("*")
            .eq("property_id", property_id)
            .gte("review_date", start_date.isoformat())
            .lte("review_date", end_date.isoformat())
        )
        
        if min_rating is not None:
            query = query.gte("rating", min_rating)
        
        response = query.order("review_date", desc=True).execute()
        
        return [Review(**item) for item in response.data]
    except Exception as e:
        logger.error(f"Error fetching reviews for {property_id}: {e}")
        return []


# ============================================================================
# WEATHER QUERIES
# ============================================================================

def get_weather_data(
    city: str,
    start_date: date,
    end_date: date
) -> List[WeatherData]:
    """
    Get weather data for a city within date range
    
    Args:
        city: City name
        start_date: Start date
        end_date: End date
        
    Returns:
        List of WeatherData models
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("weather_daily")
            .select("*")
            .eq("city", city)
            .gte("date", start_date.isoformat())
            .lte("date", end_date.isoformat())
            .order("date")
            .execute()
        )
        
        return [WeatherData(**item) for item in response.data]
    except Exception as e:
        logger.error(f"Error fetching weather data for {city}: {e}")
        return []


def detect_weather_events(weather_data: List[WeatherData]) -> Dict[str, Any]:
    """
    Detect significant weather events
    
    Args:
        weather_data: List of weather data
        
    Returns:
        Dictionary with weather event analysis
    """
    if not weather_data:
        return {"events": []}
    
    events = []
    
    # Heavy rainfall detection
    heavy_rain_days = [w for w in weather_data if w.rainfall_mm > 50]
    if heavy_rain_days:
        events.append({
            "type": "heavy_rainfall",
            "days_affected": len(heavy_rain_days),
            "max_rainfall": max(w.rainfall_mm for w in heavy_rain_days),
            "impact": "high"
        })
    
    # Extreme temperature detection
    avg_temp = sum(w.temperature for w in weather_data) / len(weather_data)
    extreme_temps = [w for w in weather_data if abs(w.temperature - avg_temp) > 10]
    if extreme_temps:
        events.append({
            "type": "extreme_temperature",
            "days_affected": len(extreme_temps),
            "impact": "medium"
        })
    
    return {
        "events": events,
        "summary": f"Found {len(events)} significant weather events"
    }


# ============================================================================
# COMPETITOR QUERIES
# ============================================================================

def get_competitors(property_id: str) -> List[Competitor]:
    """
    Get competitors for a property
    
    Args:
        property_id: Property identifier
        
    Returns:
        List of Competitor models
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("competitors")
            .select("*")
            .eq("property_id", property_id)
            .order("distance_km")
            .execute()
        )
        
        return [Competitor(**item) for item in response.data]
    except Exception as e:
        logger.error(f"Error fetching competitors for {property_id}: {e}")
        return []


def get_competitor_pricing(
    competitor_id: str,
    start_date: date,
    end_date: date
) -> List[CompetitorPricing]:
    """
    Get competitor pricing data
    
    Args:
        competitor_id: Competitor identifier
        start_date: Start date
        end_date: End date
        
    Returns:
        List of CompetitorPricing models
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("pricing_daily")
            .select("*")
            .eq("competitor_id", competitor_id)
            .gte("date", start_date.isoformat())
            .lte("date", end_date.isoformat())
            .order("date")
            .execute()
        )
        
        return [CompetitorPricing(**item) for item in response.data]
    except Exception as e:
        logger.error(f"Error fetching pricing for competitor {competitor_id}: {e}")
        return []


def analyze_price_gap(
    property_id: str,
    competitors: List[Competitor],
    property_avg_rate: float,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Analyze pricing gap with competitors
    
    Args:
        property_id: Property identifier
        competitors: List of competitors
        property_avg_rate: Property's average daily rate
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with pricing gap analysis
    """
    try:
        competitor_rates = []
        
        for comp in competitors:
            pricing = get_competitor_pricing(comp.id, start_date, end_date)
            if pricing:
                avg_comp_rate = sum(p.avg_price for p in pricing) / len(pricing)
                competitor_rates.append({
                    "competitor_name": comp.name,
                    "avg_rate": avg_comp_rate,
                    "distance_km": comp.distance_km
                })
        
        if not competitor_rates:
            return {"error": "No competitor pricing data available"}
        
        avg_competitor_rate = sum(c["avg_rate"] for c in competitor_rates) / len(competitor_rates)
        price_gap = property_avg_rate - avg_competitor_rate
        price_gap_percentage = (price_gap / avg_competitor_rate * 100) if avg_competitor_rate > 0 else 0
        
        return {
            "property_rate": round(property_avg_rate, 2),
            "avg_competitor_rate": round(avg_competitor_rate, 2),
            "price_gap": round(price_gap, 2),
            "price_gap_percentage": round(price_gap_percentage, 2),
            "positioning": "premium" if price_gap > 0 else "competitive",
            "competitor_details": competitor_rates
        }
    except Exception as e:
        logger.error(f"Error analyzing price gap: {e}")
        return {"error": str(e)}


# ============================================================================
# AMENITIES QUERIES
# ============================================================================

def get_property_amenities(property_id: str) -> Dict[str, bool]:
    """
    Get property amenities
    
    Args:
        property_id: Property identifier
        
    Returns:
        Dictionary of amenity -> availability
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("property_amenities")
            .select("amenity, available")
            .eq("entity_id", property_id)
            .execute()
        )
        
        return {item["amenity"]: item["available"] for item in response.data}
    except Exception as e:
        logger.error(f"Error fetching amenities for {property_id}: {e}")
        return {}


def compare_amenities(property_id: str, competitors: List[Competitor]) -> Dict[str, Any]:
    """
    Compare property amenities with competitors
    
    Args:
        property_id: Property identifier
        competitors: List of competitors
        
    Returns:
        Dictionary with amenity comparison
    """
    try:
        property_amenities = get_property_amenities(property_id)
        
        competitor_amenities = {}
        for comp in competitors:
            competitor_amenities[comp.name] = get_property_amenities(comp.id)
        
        # Find common amenities
        all_amenities = set(property_amenities.keys())
        for comp_amen in competitor_amenities.values():
            all_amenities.update(comp_amen.keys())
        
        # Calculate gaps
        gaps = []
        for amenity in all_amenities:
            property_has = property_amenities.get(amenity, False)
            competitor_count = sum(
                1 for comp_amen in competitor_amenities.values()
                if comp_amen.get(amenity, False)
            )
            
            if not property_has and competitor_count > 0:
                gaps.append({
                    "amenity": amenity,
                    "competitor_coverage": f"{competitor_count}/{len(competitors)}"
                })
        
        return {
            "property_amenities": property_amenities,
            "gaps": gaps,
            "gap_count": len(gaps)
        }
    except Exception as e:
        logger.error(f"Error comparing amenities: {e}")
        return {"error": str(e)}
