"""
Dashboard Service

Handles dashboard metrics and portfolio feed data
"""

from typing import List
from datetime import date, timedelta
from loguru import logger

from api.models.responses import (
    DashboardMetrics,
    PropertySummary,
    PortfolioFeedResponse,
    PropertyStatusEnum
)
from src.database.queries import (
    get_all_properties,
    get_booking_trends,
    calculate_occupancy_drop
)


class DashboardService:
    """Service for dashboard data"""
    
    @staticmethod
    def get_dashboard_metrics() -> DashboardMetrics:
        """
        Get main dashboard metrics
        
        Returns:
            DashboardMetrics with portfolio statistics
        """
        try:
            properties = get_all_properties()
            
            if not properties:
                return DashboardMetrics(
                    avg_occupancy=0.0,
                    occupancy_change=0.0,
                    projected_uplift=0.0,
                    active_agents=0,
                    pending_approvals=0
                )
            
            # Calculate average occupancy
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            total_occupancy = 0.0
            property_count = 0
            
            for prop in properties:
                trends = get_booking_trends(prop.id, start_date, end_date)
                if trends:
                    avg_occ = sum(t.occupancy_percentage for t in trends) / len(trends)
                    total_occupancy += avg_occ
                    property_count += 1
            
            avg_occupancy = total_occupancy / property_count if property_count > 0 else 0.0
            
            # Calculate change vs last month (simplified - would need more data)
            occupancy_change = 4.1  # Placeholder - calculate from historical data
            
            # Projected uplift (from AI recommendations)
            projected_uplift = 8.5  # This would come from stored impact predictions
            
            # Active agents (analysis in progress)
            active_agents = 18  # Track from analysis jobs
            pending_approvals = 4  # Track from action approval system
            
            return DashboardMetrics(
                avg_occupancy=round(avg_occupancy, 1),
                occupancy_change=occupancy_change,
                projected_uplift=projected_uplift,
                active_agents=active_agents,
                pending_approvals=pending_approvals
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            raise
    
    @staticmethod
    def get_portfolio_feed() -> PortfolioFeedResponse:
        """
        Get live portfolio feed with property summaries
        
        Returns:
            PortfolioFeedResponse with all properties
        """
        try:
            properties = get_all_properties()
            
            if not properties:
                return PortfolioFeedResponse(
                    properties=[],
                    total_properties=0,
                    live_connection_status="stable"
                )
            
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            property_summaries = []
            
            for prop in properties:
                # Get booking trends
                trends = get_booking_trends(prop.id, start_date, end_date)
                
                if not trends:
                    continue
                
                # Calculate current occupancy
                current_occupancy = sum(t.occupancy_percentage for t in trends[-7:]) / 7 if len(trends) >= 7 else 0
                
                # Calculate RevPAR
                avg_rate = sum(t.avg_daily_rate for t in trends[-7:]) / 7 if len(trends) >= 7 else 0
                revpar = (current_occupancy / 100) * avg_rate if avg_rate > 0 else 0
                
                # Determine status
                drop_metrics = calculate_occupancy_drop(prop.id, end_date, 30)
                
                if drop_metrics.get("trend") == "declining" and drop_metrics.get("drop_percentage", 0) > 5:
                    status = PropertyStatusEnum.CRITICAL
                elif drop_metrics.get("drop_percentage", 0) > 1:
                    status = PropertyStatusEnum.AT_RISK
                else:
                    status = PropertyStatusEnum.HEALTHY
                
                # Recommendations count (placeholder - would come from stored analyses)
                recommendations_count = 3 if status == PropertyStatusEnum.CRITICAL else 1 if status == PropertyStatusEnum.AT_RISK else 0
                
                property_summaries.append(PropertySummary(
                    property_id=prop.id,
                    name=prop.name,
                    city=prop.city,
                    status=status,
                    occupancy=round(current_occupancy, 0),
                    revpar=round(revpar, 0),
                    recommendations_count=recommendations_count,
                    last_analyzed=end_date if recommendations_count > 0 else None
                ))
            
            return PortfolioFeedResponse(
                properties=property_summaries,
                total_properties=len(property_summaries),
                live_connection_status="stable"
            )
            
        except Exception as e:
            logger.error(f"Error getting portfolio feed: {e}")
            raise
