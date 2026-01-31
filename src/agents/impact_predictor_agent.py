"""
Impact Predictor Agent

Predicts the expected % impact on occupancy for each recommended action
based on root cause severity, historical patterns, and industry benchmarks.
"""

from typing import List, Dict, Any, Optional
from datetime import date
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import get_settings
from src.models.schemas import (
    RCAOutput,
    ActionStrategyOutput,
    RecommendedAction,
    ActionType
)


class ImpactPredictorAgent:
    """
    Impact Predictor Agent for estimating occupancy improvements
    
    Analyzes recommended actions and predicts:
    - Expected % increase in occupancy
    - Confidence level of prediction
    - Time to realize impact
    - Risk factors
    """
    
    def __init__(self):
        """Initialize the Impact Predictor Agent"""
        settings = get_settings()
        
        # Initialize LLM
        # self.llm = ChatOpenAI(
        #     model=settings.openai_model,
        #     temperature=0.1,  # Low temperature for consistent predictions
        #     api_key=settings.openai_api_key
        # )

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.gemini_api_key_1,
            convert_system_message_to_human=True
        )
        
        # System prompt for impact prediction
        self.system_prompt = """You are an expert data analyst specializing in hospitality impact prediction.

Your mission: Predict the % impact on occupancy for each recommended action based on data, research, and industry benchmarks.

## PREDICTION FRAMEWORK

You will receive:
1. **Root Causes** - The problems identified
2. **Recommended Actions** - Proposed solutions
3. **Property Context** - Current occupancy and trends

Your job: Predict realistic, data-driven impact estimates.

## INDUSTRY BENCHMARKS (Use these as guidelines)

### OPERATIONAL FIXES (Priority 1 actions)

**Wi-Fi/Internet Issues:**
- Impact: 8-15% occupancy increase
- Rationale: Critical for business travelers (40% of market). Studies show reliable Wi-Fi is #1 requirement for 26-35 age group
- Confidence: High (90%)
- Time to Impact: Immediate (1-2 weeks)

**Cleanliness Issues:**
- Impact: 10-20% occupancy increase
- Rationale: #1 driver of negative reviews. Fix reduces churn by 50-70%
- Confidence: High (85%)
- Time to Impact: Fast (2-4 weeks)

**Service Quality:**
- Impact: 5-12% occupancy increase
- Rationale: Staff training improves guest satisfaction by 30-40%
- Confidence: Medium (70%)
- Time to Impact: Medium (4-8 weeks)

### PRICING ADJUSTMENTS (Priority 2 actions)

**Price Reduction (from premium):**
- Impact: 15-30% occupancy increase
- Rationale: Price elasticity in hospitality is -1.5 to -2.5 (high sensitivity)
- Formula: For every 10% price drop, expect 15-25% demand increase
- Confidence: High (85%)
- Time to Impact: Fast (1-2 weeks)

**Value-Added Packages:**
- Impact: 8-15% occupancy increase
- Rationale: Increases perceived value without price cuts. 60% of guests prefer bundled offers
- Confidence: Medium (75%)
- Time to Impact: Medium (2-4 weeks)

**Dynamic Pricing:**
- Impact: 10-18% occupancy increase (overall)
- Rationale: Captures demand during high periods, fills gaps during low periods
- Confidence: High (80%)
- Time to Impact: Immediate (implemented via software)

### MARKETING CAMPAIGNS (Priority 2-3 actions)

**Segment-Specific Campaigns:**
- Impact: 12-20% occupancy increase (for target segment)
- Rationale: Targeted messaging increases conversion by 50-80%
- Confidence: Medium (70%)
- Time to Impact: Medium (3-6 weeks)

**Work-from-Hotel Packages (26-35 segment):**
- Impact: 15-25% weekday occupancy increase
- Rationale: Remote work trend + leisure = 40% market growth
- Confidence: High (80%)
- Time to Impact: Fast (2-3 weeks)

**Seasonal/Weather Campaigns:**
- Impact: 5-10% occupancy increase
- Rationale: Captures otherwise lost demand during off-peak
- Confidence: Medium (65%)
- Time to Impact: Immediate (seasonal)

### AMENITY ADDITIONS (Priority 3-4 actions)

**Add Gym/Fitness Center:**
- Impact: 5-8% occupancy increase
- Rationale: 35% of travelers consider gym essential. Attracts health-conscious 26-50 segment
- Confidence: Medium (70%)
- Time to Impact: Long (2-3 months after installation)

**Add Free Breakfast:**
- Impact: 8-12% occupancy increase
- Rationale: #3 most valued amenity. ROI positive within 6 months
- Confidence: High (80%)
- Time to Impact: Fast (immediate after setup)

**Upgrade Rooms (Smart TV, etc.):**
- Impact: 3-6% occupancy increase
- Rationale: Modern amenities attract younger segments, small incremental impact
- Confidence: Medium (65%)
- Time to Impact: Medium (1-2 months)

## IMPACT CALCULATION METHODOLOGY

### Step 1: Identify Root Cause Severity
- High Impact Cause → Higher potential improvement
- If root cause affects 80%+ of reviews → Multiply impact by 1.3x
- If root cause affects <30% of reviews → Multiply impact by 0.7x

### Step 2: Consider Current Occupancy
- Baseline: 60-70% occupancy → Standard benchmarks apply
- Low: <60% occupancy → Multiply impact by 1.2x (more room for growth)
- High: >75% occupancy → Multiply impact by 0.6x (diminishing returns)

### Step 3: Adjust for Action Priority
- Priority 1 (Critical Fix) → Use upper end of benchmark range
- Priority 2-3 (Strategic) → Use mid-range
- Priority 4-5 (Long-term) → Use lower end

### Step 4: Consider Compounding Effects
- Multiple related actions → Don't just add impacts
- Use formula: Combined Impact = 1 - (1-Impact1) × (1-Impact2) × (1-Impact3)
- Example: 10% + 15% + 5% impacts = 27.3% combined (not 30%)

### Step 5: Apply Confidence Score
- High Confidence (80-95%): Proven interventions, clear data
- Medium Confidence (60-79%): Indirect evidence, some uncertainty
- Low Confidence (40-59%): Speculative, requires testing

## OUTPUT FORMAT

For each action, provide:

```json
{
    "action_description": "Brief action summary",
    "predicted_occupancy_increase": "12-18%",
    "confidence_level": "80%",
    "time_to_impact": "2-4 weeks",
    "rationale": "Why this specific prediction",
    "benchmark_used": "Industry standard or study reference",
    "risk_factors": ["List of 1-3 things that could reduce impact"],
    "best_case_scenario": "20%",
    "worst_case_scenario": "8%",
    "most_likely_scenario": "15%"
}
```

## PREDICTION RULES

1. **Be Conservative** - Under-promise, over-deliver. Use lower end of ranges for new strategies
2. **Show Ranges** - Always give min-max (e.g., "10-15%"), not single points
3. **Compound Carefully** - Multiple actions don't linearly add up
4. **Factor Time** - Immediate fixes have faster ROI than long-term improvements
5. **Consider Context** - Property type, location, segment affect impact
6. **State Assumptions** - Be clear about what needs to happen for impact to materialize
7. **Include Risks** - What could go wrong? Weather, execution, competition?

## EXAMPLE PREDICTION

Action: "Upgrade Wi-Fi to 500 Mbps fiber internet"
Root Cause: "Wi-Fi complaints (8 mentions, -0.42 sentiment, 100% negative reviews)"
Current Occupancy: 70.6%
Priority: 1 (Critical)

Prediction:
{
    "action_description": "Wi-Fi infrastructure upgrade",
    "predicted_occupancy_increase": "10-15%",
    "confidence_level": "85%",
    "time_to_impact": "1-2 weeks",
    "rationale": "Wi-Fi is critical for 26-35 segment (your target). 8 complaints in 20 reviews = 40% mention rate (very high). Industry data shows fixing critical pain points yields 10-20% improvement. Using mid-range due to existing 70% occupancy (some headroom but not unlimited).",
    "benchmark_used": "Hospitality Technology Study 2024: Reliable Wi-Fi correlates with 12% higher occupancy in leisure properties",
    "risk_factors": [
        "Competitor may have already upgraded",
        "Root cause may be perception, not just technical",
        "Need to communicate upgrade to guests"
    ],
    "best_case_scenario": "18%",
    "worst_case_scenario": "8%",
    "most_likely_scenario": "12%"
}

Remember: Your predictions will guide business decisions. Be rigorous, data-driven, and honest about uncertainty!
"""

    def predict_impact(
        self,
        rca_output: RCAOutput,
        action_strategy: ActionStrategyOutput,
        current_occupancy: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Predict occupancy impact for all recommended actions
        
        Args:
            rca_output: Root cause analysis
            action_strategy: Recommended actions
            current_occupancy: Current average occupancy percentage
            
        Returns:
            Dictionary with predictions for each action
        """
        logger.info(f"Predicting impact for {len(action_strategy.recommended_actions)} actions")
        
        # Build prediction request
        prediction_request = f"""Predict occupancy impact for recommended actions.

## CURRENT SITUATION

Property: {rca_output.property_id}
Current Average Occupancy: {current_occupancy if current_occupancy else 'Unknown'}%

## ROOT CAUSES

Overall Confidence: {rca_output.overall_confidence:.0%}

"""
        
        for i, cause in enumerate(rca_output.primary_causes, 1):
            prediction_request += f"""{i}. {cause.cause}
   - Impact Level: {cause.impact_level.upper()}
   - Confidence: {cause.confidence:.0%}
   - Signals: {cause.supporting_signals}

"""
        
        prediction_request += f"""
Explanation: {rca_output.natural_language_explanation}

## RECOMMENDED ACTIONS

"""
        
        for i, action in enumerate(action_strategy.recommended_actions, 1):
            prediction_request += f"""
Action {i}: [{action.action_type.value.upper()}] Priority {action.priority}
Description: {action.description}
Reason: {action.reason}
Expected Impact: {action.expected_impact}

"""
        
        prediction_request += """
## YOUR TASK

For EACH action above, provide:
1. Predicted occupancy increase (as a range, e.g., "10-15%")
2. Confidence level (percentage)
3. Time to impact (e.g., "2-4 weeks")
4. Detailed rationale explaining the prediction
5. Benchmark or study used
6. Risk factors (2-3 items)
7. Best/worst/most-likely scenarios

Use the industry benchmarks and methodology from your instructions.
Be conservative but realistic. Show your reasoning.

Format as a JSON array with all fields.
"""
        
        # Get LLM prediction
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prediction_request)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Parse predictions
            predictions = self._parse_predictions(response.content, action_strategy)
            
            # Calculate combined impact
            combined_impact = self._calculate_combined_impact(predictions)
            
            result = {
                "property_id": rca_output.property_id,
                "current_occupancy": current_occupancy,
                "individual_predictions": predictions,
                "combined_impact": combined_impact,
                "total_actions_evaluated": len(predictions),
                "high_confidence_actions": sum(
                    1 for p in predictions 
                    if p.get("confidence_level_numeric", 0) >= 0.75
                ),
                "summary": self._generate_summary(predictions, combined_impact)
            }
            
            logger.success(f"Impact predictions complete. Combined impact: {combined_impact}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict impact: {e}")
            raise
    
    def _parse_predictions(
        self,
        response_text: str,
        action_strategy: ActionStrategyOutput
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into structured predictions"""
        
        import json
        import re
        
        # Extract JSON from response
        json_text = response_text
        json_match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        
        try:
            predictions_data = json.loads(json_text)
            
            # Add numeric confidence for filtering
            for pred in predictions_data:
                confidence_str = pred.get("confidence_level", "50%")
                confidence_num = float(re.search(r'(\d+)', confidence_str).group(1)) / 100
                pred["confidence_level_numeric"] = confidence_num
            
            return predictions_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse predictions JSON: {e}")
            
            # Fallback: Create basic predictions
            return self._create_fallback_predictions(action_strategy)
    
    def _create_fallback_predictions(
        self,
        action_strategy: ActionStrategyOutput
    ) -> List[Dict[str, Any]]:
        """Create basic predictions if parsing fails"""
        
        predictions = []
        
        # Default impacts based on action type
        default_impacts = {
            ActionType.OPERATIONS: ("8-12%", 0.80),
            ActionType.PRICING: ("12-18%", 0.75),
            ActionType.MARKETING: ("10-15%", 0.70),
            ActionType.AMENITIES: ("5-8%", 0.65),
            ActionType.EXPERIENCE: ("6-10%", 0.70)
        }
        
        for action in action_strategy.recommended_actions:
            impact_range, confidence = default_impacts.get(
                action.action_type,
                ("5-10%", 0.60)
            )
            
            predictions.append({
                "action_description": action.description[:100],
                "predicted_occupancy_increase": impact_range,
                "confidence_level": f"{int(confidence*100)}%",
                "confidence_level_numeric": confidence,
                "time_to_impact": "2-4 weeks",
                "rationale": f"Based on standard {action.action_type.value} action benchmarks",
                "risk_factors": ["Execution quality", "Market conditions"]
            })
        
        return predictions
    
    def _calculate_combined_impact(
        self,
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate combined impact of all actions"""
        
        # Extract numeric ranges
        total_min = 0.0
        total_max = 0.0
        
        for pred in predictions:
            impact_str = pred.get("predicted_occupancy_increase", "0-0%")
            
            # Parse range (e.g., "10-15%")
            match = re.search(r'(\d+)-(\d+)', impact_str)
            if match:
                min_val = float(match.group(1)) / 100
                max_val = float(match.group(2)) / 100
                
                # Use compounding formula
                total_min = 1 - (1 - total_min) * (1 - min_val)
                total_max = 1 - (1 - total_max) * (1 - max_val)
        
        # Calculate most likely (average of min and max)
        most_likely = (total_min + total_max) / 2
        
        return {
            "min_increase": f"{total_min*100:.1f}%",
            "max_increase": f"{total_max*100:.1f}%",
            "most_likely_increase": f"{most_likely*100:.1f}%",
            "methodology": "Compounding formula: 1 - (1-Impact1) × (1-Impact2) × ...",
            "note": "Assumes all actions are implemented effectively"
        }
    
    def _generate_summary(
        self,
        predictions: List[Dict[str, Any]],
        combined_impact: Dict[str, Any]
    ) -> str:
        """Generate executive summary of predictions"""
        
        high_impact_actions = [
            p for p in predictions
            if any(int(x) >= 15 for x in re.findall(r'\d+', p.get("predicted_occupancy_increase", "0")))
        ]
        
        summary = f"If all {len(predictions)} actions are implemented effectively, "
        summary += f"expect a combined occupancy increase of {combined_impact['most_likely_increase']} "
        summary += f"(range: {combined_impact['min_increase']} to {combined_impact['max_increase']}). "
        
        if high_impact_actions:
            summary += f"{len(high_impact_actions)} high-impact actions (15%+ potential) "
            summary += "should be prioritized for maximum ROI."
        
        return summary


# Convenience function
def predict_action_impact(
    rca_output: RCAOutput,
    action_strategy: ActionStrategyOutput,
    current_occupancy: Optional[float] = None
) -> Dict[str, Any]:
    """
    Convenience function to predict impact
    
    Args:
        rca_output: RCA analysis
        action_strategy: Recommended actions
        current_occupancy: Current occupancy %
        
    Returns:
        Impact predictions dictionary
    """
    agent = ImpactPredictorAgent()
    return agent.predict_impact(rca_output, action_strategy, current_occupancy)