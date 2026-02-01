"""
Dashboard API Routes
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.models.responses import (
    DashboardMetrics,
    PortfolioFeedResponse,
    ErrorResponse
)
from api.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    summary="Get Dashboard Metrics",
    description="Retrieve main dashboard metrics including average occupancy, projected uplift, and active agents"
)
async def get_dashboard_metrics():
    """
    Get dashboard metrics
    
    Returns:
        DashboardMetrics with portfolio statistics
    """
    try:
        metrics = DashboardService.get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/portfolio",
    response_model=PortfolioFeedResponse,
    summary="Get Portfolio Feed",
    description="Retrieve live portfolio feed with all properties and their current status"
)
async def get_portfolio_feed():
    """
    Get portfolio feed
    
    Returns:
        PortfolioFeedResponse with all properties
    """
    try:
        feed = DashboardService.get_portfolio_feed()
        return feed
    except Exception as e:
        logger.error(f"Error getting portfolio feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
