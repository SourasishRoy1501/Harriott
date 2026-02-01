"""
Property API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import date, timedelta
from loguru import logger

from api.models.responses import (
    CompetitorComparisonResponse,
    ReviewStats,
    AmenitiesResponse,
    BookingTrendResponse,
    WeatherImpactResponse
)
from api.services.property_service import PropertyDetailService

router = APIRouter(prefix="/api/property", tags=["Property"])


@router.get(
    "/{property_id}/competitor-pricing",
    response_model=CompetitorComparisonResponse,
    summary="Get Competitor Pricing Comparison",
    description="Compare property pricing with competitors over a selected period"
)
async def get_competitor_pricing(
    property_id: str,
    days: int = Query(default=30, ge=7, le=90, description="Number of days to look back")
):
    """
    Get competitor pricing comparison
    
    Args:
        property_id: Property ID
        days: Number of days to analyze
        
    Returns:
        Competitor comparison data with pricing chart
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        comparison = PropertyDetailService.get_competitor_comparison(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting competitor pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{property_id}/reviews",
    response_model=ReviewStats,
    summary="Get Review Statistics",
    description="Get total reviews, ratings, and distribution for a property"
)
async def get_review_stats(
    property_id: str,
    days: int = Query(default=30, ge=7, le=90, description="Number of days to look back")
):
    """
    Get review statistics
    
    Args:
        property_id: Property ID
        days: Number of days to analyze
        
    Returns:
        Review statistics including ratings and recent reviews
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        stats = PropertyDetailService.get_review_stats(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Error getting review stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{property_id}/amenities",
    response_model=AmenitiesResponse,
    summary="Get Property Amenities",
    description="Get property amenities with gaps compared to competitors"
)
async def get_amenities(property_id: str):
    """
    Get property amenities
    
    Args:
        property_id: Property ID
        
    Returns:
        Amenities list with competitor comparison
    """
    try:
        amenities = PropertyDetailService.get_amenities(property_id=property_id)
        return amenities
    except Exception as e:
        logger.error(f"Error getting amenities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{property_id}/booking-trends",
    response_model=BookingTrendResponse,
    summary="Get Booking Trends",
    description="Get booking trends chart data over a selected period"
)
async def get_booking_trends(
    property_id: str,
    days: int = Query(default=30, ge=7, le=90, description="Number of days to look back")
):
    """
    Get booking trends
    
    Args:
        property_id: Property ID
        days: Number of days to analyze
        
    Returns:
        Booking trends data for charting
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        trends = PropertyDetailService.get_booking_trends(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date
        )
        return trends
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting booking trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{property_id}/weather-impact",
    response_model=WeatherImpactResponse,
    summary="Get Weather Impact",
    description="Get weather data and impact assessment for property location"
)
async def get_weather_impact(
    property_id: str,
    days: int = Query(default=30, ge=7, le=90, description="Number of days to look back")
):
    """
    Get weather impact
    
    Args:
        property_id: Property ID
        days: Number of days to analyze
        
    Returns:
        Weather data and impact assessment
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        weather = PropertyDetailService.get_weather_impact(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date
        )
        return weather
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting weather impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))
