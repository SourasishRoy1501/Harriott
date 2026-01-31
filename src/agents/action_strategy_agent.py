"""
Action Strategy Agent

Consumes RCA output and generates targeted campaigns and action plans
to address identified root causes and improve occupancy.
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
    ActionType,
    AgeSegment
)
from src.database.queries import get_property_by_id


class ActionStrategyAgent:
    """
    Action Strategy Agent for generating targeted campaigns and actions
    
    Takes RCA output and customer segment, then creates:
    - Specific campaigns to address root causes
    - Prioritized action items
    - Implementation roadmap
    - Resource requirements
    """
    
    def __init__(self):
        """Initialize the Action Strategy Agent"""
        settings = get_settings()
        
        # Initialize LLM
        # self.llm = ChatOpenAI(
        #     model=settings.openai_model,
        #     temperature=0.3,  # Slightly higher for creative campaigns
        #     api_key=settings.openai_api_key
        # )
        

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.gemini_api_key_1,
            convert_system_message_to_human=True
        )

        # System prompt for action strategy
        self.system_prompt = """You are an expert Action Strategy consultant for the hospitality industry.

Your mission: Transform root cause analysis into concrete, actionable campaigns and strategies.

## ANALYSIS FRAMEWORK

You will receive:
1. **Root Causes** - Why the property is underperforming
2. **Target Segment** - The dominant customer age group
3. **Property Context** - Category, location, amenities

Your job: Create a comprehensive action strategy with campaigns.

## ACTION STRATEGY STRUCTURE

### 1. IMMEDIATE FIXES (0-2 weeks)
Priority: Address critical issues causing negative reviews
Examples:
- Wi-Fi issues → "Upgrade internet to 500 Mbps fiber, add mesh network"
- Cleanliness → "Deep clean all rooms, implement daily quality checks"
- Service → "Retrain staff on customer service protocols"

### 2. PRICING CAMPAIGNS (2-4 weeks)
If pricing is a root cause, create specific campaigns:

**For Price Premium Issues:**
- "Value-Added Package" - Bundle amenities to justify price
- "Work-from-Hotel Deal" - Target segment-specific pricing
- "Extended Stay Discount" - Encourage longer bookings
- "Dynamic Pricing Adjustment" - Reduce rates during low demand

**For Price Too Low Issues:**
- "Premium Experience Upgrade" - Improve amenities, then increase price
- "Exclusive Member Rates" - Create tiered pricing
- "Seasonal Premium" - Adjust for demand periods

### 3. MARKETING CAMPAIGNS (2-6 weeks)
Target the dominant customer segment with specific campaigns:

**For 18-25 (Budget/Student):**
- "Student Escape Package" - Affordable rates, social activities
- "Backpacker Special" - Shared spaces, local experiences
- "Group Booking Discount" - Attract friend groups

**For 26-35 (Young Professional):**
- "Work-from-Anywhere Package" - High-speed Wi-Fi, workspace, coffee
- "Weekend Warrior Deal" - Friday check-in discounts
- "Digital Nomad Special" - Weekly rates, coworking amenities

**For 36-50 (Family/Business):**
- "Family Staycation" - Kids activities, family rooms
- "Business Travel Rewards" - Loyalty points, meeting rooms
- "Extended Family Package" - Multiple rooms, group dining

**For 50+ (Leisure):**
- "Peaceful Retreat Package" - Spa, quiet zones, comfort focus
- "Cultural Experience Tour" - Local attractions, guided tours
- "Health & Wellness Stay" - Yoga, healthy meals, relaxation

### 4. EXPERIENCE IMPROVEMENTS (1-3 months)
Long-term enhancements:
- Add missing amenities (gym, breakfast, etc.)
- Improve existing features
- Create unique experiences
- Staff training programs

### 5. WEATHER/SEASONAL STRATEGIES
If weather is a root cause:
- "Monsoon Special" - Indoor activities, cozy ambiance, discounts
- "Rain-or-Shine Package" - Guaranteed activities regardless of weather
- "Off-Season Escape" - Target weather-immune segments (business travelers)

## OUTPUT FORMAT

For each recommended action, provide:

1. **Action Type**: pricing | marketing | experience | amenities | operations
2. **Priority**: 1 (highest/urgent) to 5 (lowest/long-term)
3. **Campaign Name**: Clear, catchy, segment-specific
4. **Description**: Exactly what to do (2-3 sentences)
5. **Reason**: How this addresses the root cause (1 sentence)
6. **Target Segment**: Which age group benefits most
7. **Timeline**: When to implement (immediate, 2 weeks, 1 month, etc.)
8. **Budget**: Estimated cost (low <10K, medium 10-50K, high >50K)
9. **Expected Impact**: Brief statement of expected improvement

## CAMPAIGN CREATION RULES

1. **Be Specific** - "Upgrade Wi-Fi to 500 Mbps" not "Improve internet"
2. **Name Campaigns** - Catchy, memorable names like "Work-from-Paradise Package"
3. **Match Segment** - Align campaigns with customer age preferences
4. **Address Root Causes** - Every action must tie to an identified problem
5. **Prioritize** - Urgent fixes first, long-term improvements later
6. **Be Realistic** - Consider budget and implementation complexity
7. **Mix Quick Wins & Long-term** - Balance immediate fixes with strategic improvements

## PRIORITY GUIDELINES

**Priority 1 (Urgent):**
- Critical service failures (Wi-Fi, cleanliness)
- Major negative review themes
- Safety or hygiene issues

**Priority 2 (High):**
- Pricing adjustments
- Major amenity gaps
- Competitive positioning

**Priority 3 (Medium):**
- Marketing campaigns
- Experience enhancements
- Staff training

**Priority 4 (Low):**
- Nice-to-have amenities
- Long-term strategic improvements
- Brand positioning

**Priority 5 (Aspirational):**
- Major renovations
- New facility additions
- Market expansion

## EXAMPLE OUTPUT

Root Cause: "Wi-Fi complaints, 49% price premium, heavy rainfall"
Segment: 26-35 (Young Professional)

Actions:
1. [Priority 1] "Connectivity Crisis Fix"
   - Type: Operations
   - Description: Immediately upgrade to 500 Mbps fiber internet with mesh Wi-Fi coverage in all rooms and common areas. Add dedicated work-from-hotel bandwidth. Complete within 1 week.
   - Reason: Addresses #1 complaint (Wi-Fi) driving 100% negative reviews
   - Timeline: Immediate (1 week)
   - Budget: Medium (₹30,000)
   - Impact: Expected to reduce Wi-Fi complaints by 90%+

2. [Priority 2] "Work-from-Paradise Package"
   - Type: Marketing
   - Description: Target 26-35 professionals with bundled offer: Premium Wi-Fi + dedicated workspace + unlimited coffee + flexible check-in. Promote as "Your office in the hills" with 20% weekday discount.
   - Reason: Justifies premium pricing while addressing Wi-Fi concerns
   - Timeline: 2 weeks
   - Budget: Low (₹5,000 for marketing)
   - Impact: Expected 15-20% increase in weekday bookings

3. [Priority 2] "Monsoon Magic Deal"
   - Type: Pricing
   - Description: Offer 25% discount during heavy rain periods with "Rain-or-Shine Activities" - indoor games, movie nights, spa sessions. Guarantee refund if guest is unsatisfied.
   - Reason: Addresses weather-related booking reluctance
   - Timeline: Immediate
   - Budget: Low (revenue sharing)
   - Impact: Expected 10-15% occupancy boost during rainy periods

Remember: Every action must be specific, measurable, and directly address a root cause!
"""

    def generate_strategy(
        self,
        rca_output: RCAOutput,
        target_segment: AgeSegment,
        property_id: Optional[str] = None
    ) -> ActionStrategyOutput:
        """
        Generate action strategy based on RCA output and target segment
        
        Args:
            rca_output: Root cause analysis output
            target_segment: Dominant customer age segment
            property_id: Optional property ID for context
            
        Returns:
            ActionStrategyOutput with recommended campaigns and actions
        """
        logger.info(f"Generating action strategy for property {rca_output.property_id}")
        
        # Get property context if available
        property_context = ""
        if property_id:
            property_info = get_property_by_id(property_id)
            if property_info:
                property_context = f"""
Property Context:
- Name: {property_info.name}
- City: {property_info.city}
- Category: {property_info.category}
- Total Rooms: {property_info.total_rooms}
"""
        
        # Build the strategy request
        strategy_request = f"""Generate comprehensive action strategy.

{property_context}

## ROOT CAUSE ANALYSIS

Overall Confidence: {rca_output.overall_confidence:.0%}

Primary Root Causes:
"""
        
        for i, cause in enumerate(rca_output.primary_causes, 1):
            strategy_request += f"""
{i}. {cause.cause}
   - Confidence: {cause.confidence:.0%}
   - Impact Level: {cause.impact_level.upper()}
   - Supporting Signals: {cause.supporting_signals}
"""
        
        strategy_request += f"""

Explanation: {rca_output.natural_language_explanation}

## TARGET CUSTOMER SEGMENT

Dominant Segment: {target_segment.value}

Segment Characteristics:
"""
        
        # Add segment-specific context
        segment_profiles = {
            AgeSegment.YOUNG_ADULT: "Budget-conscious, social, value experiences over luxury, active on social media, prefer hostels/budget hotels",
            AgeSegment.YOUNG_PROFESSIONAL: "Work-life balance focused, need reliable Wi-Fi, value convenience and productivity, moderate budget, prefer modern amenities",
            AgeSegment.FAMILY_BUSINESS: "Family comfort or business efficiency, willing to pay for quality, need space and amenities, value reliability",
            AgeSegment.SENIOR: "Comfort and service focused, value peace and quiet, willing to pay premium, prefer traditional hospitality"
        }
        
        strategy_request += f"- {segment_profiles.get(target_segment, 'General traveler')}\n"
        
        strategy_request += """

## YOUR TASK

Create 5-8 specific action items that:
1. Directly address each root cause
2. Are tailored to the target segment
3. Include immediate fixes AND strategic campaigns
4. Have clear priorities, timelines, and budgets
5. Include catchy campaign names where appropriate

Focus on actionable, specific steps that can be implemented.

Format as a structured list with all required fields for each action.
"""
        
        # Get LLM response
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=strategy_request)
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Parse the response into structured actions
            actions = self._parse_actions(response.content, rca_output, target_segment)
            
            # Create output
            output = ActionStrategyOutput(
                property_id=rca_output.property_id,
                target_segment=target_segment,
                recommended_actions=actions,
                rationale=self._generate_rationale(rca_output, target_segment)
            )
            
            logger.success(f"Generated {len(actions)} action items")
            return output
            
        except Exception as e:
            logger.error(f"Failed to generate action strategy: {e}")
            raise
    
    def _parse_actions(
        self,
        response_text: str,
        rca_output: RCAOutput,
        target_segment: AgeSegment
    ) -> List[RecommendedAction]:
        """Parse LLM response into structured actions"""
        
        # Use LLM to extract structured data
        extraction_prompt = f"""Extract action items from this strategy.

Strategy Text:
{response_text}

Extract each action with:
1. action_type (pricing|marketing|experience|amenities|operations)
2. priority (1-5, where 1 is highest)
3. description (what to do)
4. reason (why this addresses root causes)
5. Optional: campaign_name, timeline, budget_estimate

Format as JSON array:
[
    {{
        "action_type": "operations",
        "priority": 1,
        "description": "Upgrade Wi-Fi to 500 Mbps...",
        "reason": "Addresses Wi-Fi complaints...",
        "campaign_name": "Connectivity Crisis Fix",
        "timeline": "1 week",
        "budget": "medium"
    }}
]
"""
        
        extraction_response = self.llm.invoke([
            SystemMessage(content="You extract structured data from text. Return only valid JSON."),
            HumanMessage(content=extraction_prompt)
        ])
        
        # Parse JSON
        import json
        import re
        
        json_text = extraction_response.content
        json_match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        
        try:
            actions_data = json.loads(json_text)
            
            actions = []
            for action_data in actions_data:
                # Map string to ActionType enum
                action_type_map = {
                    "pricing": ActionType.PRICING,
                    "marketing": ActionType.MARKETING,
                    "experience": ActionType.EXPERIENCE,
                    "amenities": ActionType.AMENITIES,
                    "operations": ActionType.OPERATIONS
                }
                
                action = RecommendedAction(
                    action_type=action_type_map.get(
                        action_data.get("action_type", "operations").lower(),
                        ActionType.OPERATIONS
                    ),
                    priority=action_data.get("priority", 3),
                    description=action_data.get("description", ""),
                    reason=action_data.get("reason", ""),
                    expected_impact=f"Timeline: {action_data.get('timeline', 'TBD')} | Budget: {action_data.get('budget', 'TBD')}",
                    implementation_complexity=action_data.get("budget", "medium")
                )
                
                actions.append(action)
            
            # Sort by priority
            actions.sort(key=lambda x: x.priority)
            
            return actions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse actions JSON: {e}")
            
            # Fallback: Create basic actions from root causes
            return self._create_fallback_actions(rca_output, target_segment)
    
    def _create_fallback_actions(
        self,
        rca_output: RCAOutput,
        target_segment: AgeSegment
    ) -> List[RecommendedAction]:
        """Create basic actions if parsing fails"""
        
        actions = []
        
        for i, cause in enumerate(rca_output.primary_causes[:3], 1):
            action = RecommendedAction(
                action_type=ActionType.OPERATIONS,
                priority=i,
                description=f"Address: {cause.cause}",
                reason=cause.cause,
                expected_impact=f"Target impact on confidence: {cause.confidence:.0%}",
                implementation_complexity="medium"
            )
            actions.append(action)
        
        return actions
    
    def _generate_rationale(
        self,
        rca_output: RCAOutput,
        target_segment: AgeSegment
    ) -> str:
        """Generate overall rationale for the strategy"""
        
        high_impact_causes = [
            c for c in rca_output.primary_causes
            if c.impact_level == "high"
        ]
        
        rationale = f"This strategy prioritizes {len(high_impact_causes)} high-impact root causes "
        rationale += f"with campaigns tailored for {target_segment.value} segment. "
        rationale += f"Actions are sequenced from immediate fixes (Priority 1) to long-term improvements, "
        rationale += f"ensuring quick wins while building sustainable improvements."
        
        return rationale


# Convenience function
def generate_action_strategy(
    rca_output: RCAOutput,
    target_segment: AgeSegment,
    property_id: Optional[str] = None
) -> ActionStrategyOutput:
    """
    Convenience function to generate action strategy
    
    Args:
        rca_output: RCA analysis output
        target_segment: Target customer segment
        property_id: Optional property ID
        
    Returns:
        ActionStrategyOutput with campaigns
    """
    agent = ActionStrategyAgent()
    return agent.generate_strategy(rca_output, target_segment, property_id)