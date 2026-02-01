"""
Property Detail Service

Handles property-specific data retrieval for detail pages
"""

from typing import List, Dict, Any
from datetime import date, timedelta
from loguru import logger

from api.models.responses import (
    CompetitorPricing,
    CompetitorComparisonResponse,
    ReviewStats,
    AmenityItem,
    AmenitiesResponse,
    BookingTrendPoint,
    BookingTrendResponse,
    WeatherDataPoint,
    WeatherImpactResponse
)
from src.database.queries import (
    get_property_by_id,
    get_booking_trends,
    get_competitors,
    get_competitor_pricing,
    analyze_price_gap,
    get_reviews,
    get_property_amenities,
    compare_amenities,
    get_weather_data,
    detect_weather_events
)


class PropertyDetailService:
    """Service for property detail data"""
    
    @staticmethod
    def get_competitor_comparison(
        property_id: str,
        start_date: date,
        end_date: date
    ) -> CompetitorComparisonResponse:
        """
        Get competitor pricing comparison
        
        Args:
            property_id: Property ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Competitor comparison data
        """
        try:
            property_info = get_property_by_id(property_id)
            if not property_info:
                raise ValueError(f"Property {property_id} not found")
            
            # Get property booking trends
            property_trends = get_booking_trends(property_id, start_date, end_date)
            if not property_trends:
                raise ValueError("No booking data available")
            
            property_avg_rate = sum(t.avg_daily_rate for t in property_trends) / len(property_trends)
            
            # Get competitors
            competitors = get_competitors(property_id)
            if not competitors:
                raise ValueError("No competitors found")
            
            # Get competitor pricing and build comparison
            pricing_data = []
            
            # Get dates from property trends
            for trend in property_trends:
                # Calculate average competitor rate for this date
                comp_rates = []
                for comp in competitors:
                    comp_pricing = get_competitor_pricing(comp.id, trend.date, trend.date)
                    if comp_pricing:
                        comp_rates.append(comp_pricing[0].avg_price)
                
                if comp_rates:
                    avg_comp_rate = sum(comp_rates) / len(comp_rates)
                    gap_pct = ((trend.avg_daily_rate - avg_comp_rate) / avg_comp_rate * 100) if avg_comp_rate > 0 else 0
                    
                    pricing_data.append(CompetitorPricing(
                        date=trend.date,
                        property_rate=round(trend.avg_daily_rate, 2),
                        competitor_avg_rate=round(avg_comp_rate, 2),
                        gap_percentage=round(gap_pct, 2)
                    ))
            
            # Calculate average gap
            avg_gap = sum(p.gap_percentage for p in pricing_data) / len(pricing_data) if pricing_data else 0
            
            # Determine positioning
            if avg_gap > 10:
                positioning = "premium"
            elif avg_gap < -10:
                positioning = "budget"
            else:
                positioning = "competitive"
            
            return CompetitorComparisonResponse(
                property_id=property_id,
                property_name=property_info.name,
                period_start=start_date,
                period_end=end_date,
                pricing_data=pricing_data,
                avg_gap_percentage=round(avg_gap, 2),
                positioning=positioning
            )
            
        except Exception as e:
            logger.error(f"Error getting competitor comparison: {e}")
            raise
    
    @staticmethod
    def get_review_stats(
        property_id: str,
        start_date: date,
        end_date: date
    ) -> ReviewStats:
        """
        Get review statistics
        
        Args:
            property_id: Property ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Review statistics
        """
        try:
            reviews = get_reviews(property_id, start_date, end_date)
            
            if not reviews:
                return ReviewStats(
                    total_reviews=0,
                    avg_rating=0.0,
                    rating_distribution={},
                    recent_reviews=[]
                )
            
            # Calculate stats
            total = len(reviews)
            avg_rating = sum(r.rating for r in reviews) / total
            
            # Rating distribution
            distribution = {}
            for i in range(1, 6):
                count = sum(1 for r in reviews if r.rating == i)
                distribution[str(i)] = count
            
            # Recent reviews (last 5)
            recent = [
                {
                    "rating": r.rating,
                    "text": r.review_text[:150] + "..." if len(r.review_text) > 150 else r.review_text,
                    "date": str(r.review_date)
                }
                for r in sorted(reviews, key=lambda x: x.review_date, reverse=True)[:5]
            ]
            
            return ReviewStats(
                total_reviews=total,
                avg_rating=round(avg_rating, 1),
                rating_distribution=distribution,
                recent_reviews=recent
            )
            
        except Exception as e:
            logger.error(f"Error getting review stats: {e}")
            raise
    
    @staticmethod
    def get_amenities(property_id: str) -> AmenitiesResponse:
        """
        Get property amenities with gaps
        
        Args:
            property_id: Property ID
            
        Returns:
            Amenities data
        """
        try:
            # Get property amenities
            property_amen = get_property_amenities(property_id)
            
            # Get competitors for comparison
            competitors = get_competitors(property_id)
            
            # Compare amenities
            comparison = compare_amenities(property_id, competitors) if competitors else {"gaps": [], "gap_count": 0}
            
            # Build amenity items
            amenity_items = []
            for name, available in property_amen.items():
                # Check if in gaps
                comp_coverage = None
                for gap in comparison.get("gaps", []):
                    if gap["amenity"].lower() == name.lower():
                        comp_coverage = gap["competitor_coverage"]
                        break
                
                amenity_items.append(AmenityItem(
                    name=name,
                    available=available,
                    competitor_coverage=comp_coverage
                ))
            
            # Identify critical missing amenities
            critical_amenities = ["WiFi", "Gym", "Breakfast", "Parking"]
            missing_critical = [
                item.name for item in amenity_items
                if not item.available and any(crit.lower() in item.name.lower() for crit in critical_amenities)
            ]
            
            return AmenitiesResponse(
                property_id=property_id,
                amenities=amenity_items,
                missing_critical=missing_critical,
                gap_count=comparison.get("gap_count", 0)
            )
            
        except Exception as e:
            logger.error(f"Error getting amenities: {e}")
            raise
    
    @staticmethod
    def get_booking_trends(
        property_id: str,
        start_date: date,
        end_date: date
    ) -> BookingTrendResponse:
        """
        Get booking trends chart data
        
        Args:
            property_id: Property ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Booking trends data
        """
        try:
            trends = get_booking_trends(property_id, start_date, end_date)
            
            if not trends:
                raise ValueError("No booking data available")
            
            # Convert to response format
            trend_points = [
                BookingTrendPoint(
                    date=t.date,
                    occupancy=round(t.occupancy_percentage, 1),
                    bookings=t.bookings,
                    avg_rate=round(t.avg_daily_rate, 2)
                )
                for t in trends
            ]
            
            # Calculate average occupancy
            avg_occ = sum(t.occupancy for t in trend_points) / len(trend_points)
            
            # Determine trend direction
            first_half = trend_points[:len(trend_points)//2]
            second_half = trend_points[len(trend_points)//2:]
            
            first_avg = sum(t.occupancy for t in first_half) / len(first_half) if first_half else 0
            second_avg = sum(t.occupancy for t in second_half) / len(second_half) if second_half else 0
            
            if second_avg > first_avg + 2:
                trend_direction = "improving"
            elif second_avg < first_avg - 2:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
            
            return BookingTrendResponse(
                property_id=property_id,
                period_start=start_date,
                period_end=end_date,
                trends=trend_points,
                avg_occupancy=round(avg_occ, 1),
                trend_direction=trend_direction
            )
            
        except Exception as e:
            logger.error(f"Error getting booking trends: {e}")
            raise
    
    @staticmethod
    def get_weather_impact(
        property_id: str,
        start_date: date,
        end_date: date
    ) -> WeatherImpactResponse:
        """
        Get weather impact data
        
        Args:
            property_id: Property ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Weather impact data
        """
        try:
            property_info = get_property_by_id(property_id)
            if not property_info:
                raise ValueError(f"Property {property_id} not found")
            
            # Get weather data
            weather_data = get_weather_data(property_info.city, start_date, end_date)
            
            if not weather_data:
                raise ValueError("No weather data available")
            
            # Convert to response format
            weather_points = [
                WeatherDataPoint(
                    date=w.date,
                    weather_type=w.weather_type,
                    temperature=round(w.temperature, 1),
                    rainfall_mm=round(w.rainfall_mm, 1)
                )
                for w in weather_data
            ]
            
            # Detect events
            events_dict = detect_weather_events(weather_data)
            
            # Count rainy days
            rainy_days = sum(1 for w in weather_data if w.rainfall_mm > 10)
            
            # Assess impact
            impact = "low"
            if rainy_days > len(weather_data) * 0.5:
                impact = "high"
            elif rainy_days > len(weather_data) * 0.3:
                impact = "medium"
            
            return WeatherImpactResponse(
                property_id=property_id,
                city=property_info.city,
                period_start=start_date,
                period_end=end_date,
                weather_data=weather_points,
                rainy_days=rainy_days,
                extreme_events=events_dict.get("events", []),
                impact_assessment=impact
            )
            
        except Exception as e:
            logger.error(f"Error getting weather impact: {e}")
            raise
