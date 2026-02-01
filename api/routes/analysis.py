"""
Analysis API Routes
"""

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from datetime import date
from loguru import logger
from typing import Dict
import uuid

from api.models.responses import (
    AnalysisRequest,
    AnalysisStatus,
    CompleteAnalysisResponse
)
from api.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post(
    "/start",
    response_model=Dict[str, str],
    summary="Start Property Analysis",
    description="Start AI analysis workflow for a property (RCA + Actions + Impact)"
)
async def start_analysis(request: AnalysisRequest = Body(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Start property analysis
    
    This triggers the complete AI workflow:
    1. RCA Agent - Identifies root causes
    2. Action Strategy Agent - Generates campaigns
    3. Impact Predictor Agent - Forecasts occupancy impact
    
    Args:
        request: Analysis request with property_id and parameters
        
    Returns:
        Analysis ID for tracking progress
    """
    try:
        analysis_date = request.analysis_date if request.analysis_date else date.today()
        
        analysis_id = str(uuid.uuid4())

         # Fire-and-forget analysis
        background_tasks.add_task(
            AnalysisService.start_analysis,
            analysis_id,
            request.property_id,
            analysis_date,
            request.lookback_days
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "started",
            "message": "Analysis started successfully"
        }
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{analysis_id}/status",
    response_model=AnalysisStatus,
    summary="Get Analysis Status",
    description="Check the status of a running analysis"
)
async def get_analysis_status(analysis_id: str):
    """
    Get analysis status
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Current status and progress of analysis
    """
    try:
        status = AnalysisService.get_analysis_status(analysis_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{analysis_id}/result",
    response_model=CompleteAnalysisResponse,
    summary="Get Analysis Result",
    description="Get complete analysis result including RCA, actions, and impact predictions"
)
async def get_analysis_result(analysis_id: str):
    """
    Get complete analysis result
    
    This returns the full analysis including:
    - Root Cause Analysis (RCA)
    - Recommended Actions
    - Impact Predictions
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Complete analysis result
    """
    try:
        result = AnalysisService.get_analysis_result(analysis_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting analysis result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from typing import Dict
