"""
Analysis Service

Handles property analysis workflow with all AI agents
"""

from typing import Dict, Any
from datetime import date, datetime
from loguru import logger
import uuid
import json

from api.models.responses import (
    AnalysisStatus,
    RCAOutputResponse,
    RootCauseItem,
    ActionStrategyResponse,
    RecommendedActionCard,
    ImpactPredictionResponse,
    ImpactPrediction,
    CombinedImpact,
    CompleteAnalysisResponse
)
from src.agents.rca_agent import analyze_property_rca
from src.agents.action_strategy_agent import generate_action_strategy
from src.agents.impact_predictor_agent import predict_action_impact
from src.models.schemas import AgeSegment
from src.database.queries import get_property_by_id, calculate_occupancy_drop


# In-memory storage for analysis jobs (would be Redis/DB in production)
analysis_jobs: Dict[str, Dict[str, Any]] = {}


class AnalysisService:
    """Service for property analysis"""
    
    @staticmethod
    def start_analysis(
        analysis_id: str,
        property_id: str,
        analysis_date: date,
        lookback_days: int = 30
    ) -> str:
        """
        Start property analysis (async)
        
        Args:
            property_id: Property to analyze
            analysis_date: Analysis date
            lookback_days: Days to look back
            
        Returns:
            Analysis ID for tracking
        """
        try:
            
            # Create job record
            analysis_jobs[analysis_id] = {
                "analysis_id": analysis_id,
                "property_id": property_id,
                "status": "queued",
                "progress": 0,
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
                "error_message": None,
                "result": None
            }
            
            # In production, this would be sent to a task queue (Celery, etc.)
            # For now, we'll process synchronously
            try:
                result = AnalysisService._run_analysis(
                    property_id,
                    analysis_date,
                    lookback_days,
                    analysis_id
                )
                
                # Update job
                analysis_jobs[analysis_id]["status"] = "completed"
                analysis_jobs[analysis_id]["progress"] = 100
                analysis_jobs[analysis_id]["completed_at"] = datetime.now().isoformat()
                analysis_jobs[analysis_id]["result"] = result
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                analysis_jobs[analysis_id]["status"] = "failed"
                analysis_jobs[analysis_id]["error_message"] = str(e)
            
            return analysis_id
            
        except Exception as e:
            logger.error(f"Error starting analysis: {e}")
            raise
    
    @staticmethod
    def _run_analysis(
        property_id: str,
        analysis_date: date,
        lookback_days: int,
        analysis_id: str
    ) -> Dict[str, Any]:
        """
        Run complete analysis workflow
        
        Args:
            property_id: Property to analyze
            analysis_date: Analysis date
            lookback_days: Days to look back
            analysis_id: Analysis job ID
            
        Returns:
            Complete analysis result
        """
        logger.info(f"Starting analysis {analysis_id} for property {property_id}")
        
        # Update progress
        analysis_jobs[analysis_id]["status"] = "processing"
        analysis_jobs[analysis_id]["progress"] = 10
        
        # Step 1: RCA
        logger.info("Running RCA Agent...")
        rca_result = analyze_property_rca(property_id, analysis_date, lookback_days)
        analysis_jobs[analysis_id]["progress"] = 40
        
        # Step 2: Action Strategy (using default segment for now)
        logger.info("Running Action Strategy Agent...")
        # In production, would use Segmentation Agent to determine this
        target_segment = AgeSegment.YOUNG_PROFESSIONAL
        
        action_strategy = generate_action_strategy(
            rca_output=rca_result,
            target_segment=target_segment,
            property_id=property_id
        )
        analysis_jobs[analysis_id]["progress"] = 70
        
        # Step 3: Impact Prediction
        logger.info("Running Impact Predictor Agent...")
        
        # Get current occupancy
        drop_metrics = calculate_occupancy_drop(property_id, analysis_date, lookback_days)
        current_occupancy = drop_metrics.get("first_period_avg", 70.0)
        
        impact_prediction = predict_action_impact(
            rca_output=rca_result,
            action_strategy=action_strategy,
            current_occupancy=current_occupancy
        )
        analysis_jobs[analysis_id]["progress"] = 90
        
        # Build complete response
        property_info = get_property_by_id(property_id)
        
        complete_result = {
            "analysis_id": analysis_id,
            "property_id": property_id,
            "property_name": property_info.name if property_info else "Unknown",
            "analysis_date": str(analysis_date),
            "current_occupancy": current_occupancy,
            "rca": rca_result,
            "actions": action_strategy,
            "impact": impact_prediction,
            "status": "completed",
            "generated_at": datetime.now().isoformat()
        }
        
        logger.success(f"Analysis {analysis_id} completed successfully")
        
        return complete_result
    
    @staticmethod
    def get_analysis_status(analysis_id: str) -> AnalysisStatus:
        """
        Get analysis job status
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis status
        """
        if analysis_id not in analysis_jobs:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        job = analysis_jobs[analysis_id]
        
        return AnalysisStatus(
            analysis_id=job["analysis_id"],
            property_id=job["property_id"],
            status=job["status"],
            progress=job["progress"],
            started_at=job["started_at"],
            completed_at=job["completed_at"],
            error_message=job["error_message"]
        )
    
    @staticmethod
    def get_analysis_result(analysis_id: str) -> CompleteAnalysisResponse:
        """
        Get complete analysis result
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Complete analysis response
        """
        if analysis_id not in analysis_jobs:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        job = analysis_jobs[analysis_id]
        
        if job["status"] != "completed":
            raise ValueError(f"Analysis {analysis_id} not completed yet")
        
        if not job["result"]:
            raise ValueError(f"No result available for analysis {analysis_id}")
        
        result = job["result"]
        
        # Convert RCA output
        rca_output = result["rca"]
        rca_response = RCAOutputResponse(
            property_id=rca_output.property_id,
            analysis_date=rca_output.analysis_date,
            overall_confidence=rca_output.overall_confidence,
            primary_causes=[
                RootCauseItem(
                    cause=cause.cause,
                    confidence=cause.confidence,
                    impact_level=cause.impact_level,
                    supporting_signals=cause.supporting_signals
                )
                for cause in rca_output.primary_causes
            ],
            explanation=rca_output.natural_language_explanation,
            review_themes=[],
            competitor_gaps=[],
            weather_impact=None
        )
        
        # Convert Action Strategy
        actions = result["actions"]
        action_response = ActionStrategyResponse(
            property_id=actions.property_id,
            target_segment=actions.target_segment.value,
            recommended_actions=[
                RecommendedActionCard(
                    action_id=f"action_{i}",
                    action_type=action.action_type,
                    priority=action.priority,
                    campaign_name=None,  # Extract from description if available
                    description=action.description,
                    reason=action.reason,
                    timeline=None,  # Extract from expected_impact if available
                    budget_estimate=action.implementation_complexity,
                    predicted_uplift=action.expected_impact.split("|")[0].strip() if "|" in action.expected_impact else None,
                    confidence=None
                )
                for i, action in enumerate(actions.recommended_actions, 1)
            ],
            total_actions=len(actions.recommended_actions),
            priority_1_count=sum(1 for a in actions.recommended_actions if a.priority == 1),
            rationale=actions.rationale
        )
        
        # Convert Impact Prediction
        impact = result["impact"]
        impact_response = ImpactPredictionResponse(
            property_id=impact["property_id"],
            current_occupancy=impact["current_occupancy"],
            projected_occupancy=impact["current_occupancy"] + float(impact["combined_impact"]["most_likely_increase"].strip("%")),
            individual_predictions=[
                ImpactPrediction(
                    action_description=pred["action_description"],
                    predicted_increase=pred["predicted_occupancy_increase"],
                    confidence_level=pred["confidence_level"],
                    time_to_impact=pred.get("time_to_impact", "TBD"),
                    rationale=pred.get("rationale", ""),
                    risk_factors=pred.get("risk_factors", [])
                )
                for pred in impact["individual_predictions"]
            ],
            combined_impact=CombinedImpact(
                min_increase=impact["combined_impact"]["min_increase"],
                max_increase=impact["combined_impact"]["max_increase"],
                most_likely_increase=impact["combined_impact"]["most_likely_increase"],
                methodology=impact["combined_impact"]["methodology"]
            ),
            summary=impact["summary"],
            high_confidence_actions=impact["high_confidence_actions"]
        )
        
        return CompleteAnalysisResponse(
            analysis_id=result["analysis_id"],
            property_id=result["property_id"],
            property_name=result["property_name"],
            analysis_date=date.fromisoformat(result["analysis_date"]),
            current_occupancy=result["current_occupancy"],
            rca=rca_response,
            actions=action_response,
            impact=impact_response,
            status=result["status"],
            generated_at=result["generated_at"]
        )
