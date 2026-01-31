"""
Root Cause Analysis (RCA) Agent

Core responsibility: Diagnose WHY a property is underperforming by analyzing:
1. Booking data trends (over/underperformance)
2. Guest reviews and sentiment
3. Competitor positioning
4. Weather impact

The agent orchestrates multiple tools to correlate signals and identify root causes.
"""

from typing import Dict, Any, List, Optional
from datetime import date
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config.settings import get_settings
from src.tools import all_tools
from src.models.schemas import (
    RCAOutput, 
    RootCause, 
    ReviewTheme, 
    CompetitorGap,
    PropertyStatus
)
from src.database.queries import get_property_by_id


class RCAAgent:
    """
    Root Cause Analysis Agent for property occupancy diagnosis
    
    Executes 4 core analysis tasks:
    1. Booking Analysis - Identify over/underperformance
    2. Review Analysis - Extract sentiment and themes
    3. Competitor Analysis - Compare pricing and amenities
    4. Weather Analysis - Detect travel deterrents
    """
    
    def __init__(self):
        """Initialize the RCA Agent"""
        settings = get_settings()
        
        # Initialize LLM
        # self.llm = ChatOpenAI(
        #     model=settings.openai_model,
        #     temperature=settings.llm_temperature,
        #     api_key=settings.openai_api_key
        # )

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.gemini_api_key,
            convert_system_message_to_human=True
        )

        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(all_tools)
        
        # System prompt for RCA
        self.system_prompt = """You are an expert Root Cause Analysis agent for hotel occupancy.

Your mission: Diagnose WHY a property is underperforming by executing 4 core analysis tasks.

## ANALYSIS FRAMEWORK

### Task 1: BOOKING ANALYSIS (Must do first)
Goal: Determine if property is over/underperforming
Tools to use:
- get_occupancy_trends: Get overall occupancy patterns
- analyze_occupancy_drop: Calculate drop percentage and trend
- check_weekday_weekend_pattern: Identify stay pattern issues

Key questions:
- What's the occupancy trend? (improving/stable/declining)
- How significant is the drop? (>10% = significant)
- Is it weekday or weekend specific?

### Task 2: REVIEW ANALYSIS (Must do second)
Goal: Extract guest sentiment and identify specific problems
Tools to use:
- analyze_review_themes: Get top themes with sentiment
- get_negative_review_insights: Focus on complaints
- analyze_review_sentiment_trend: Track sentiment changes
- get_rating_distribution: Understand rating patterns

Key questions:
- What are guests complaining about most?
- Which issues have negative sentiment?
- Is sentiment getting worse over time?
- Are there recurring themes? (Wi-Fi, cleanliness, service)

### Task 3: COMPETITOR ANALYSIS (Must do third)
Goal: Understand competitive position
Tools to use:
- analyze_competitor_pricing: Compare pricing strategy
- compare_property_amenities: Identify amenity gaps
- get_competitor_context: Understand competitive pressure

Key questions:
- Are we priced too high or too low?
- What amenities are competitors offering that we're not?
- How intense is the competitive pressure?

### Task 4: WEATHER ANALYSIS (Must do fourth)
Goal: Detect external travel deterrents
Tools to use:
- analyze_weather_impact: Assess overall weather impact
- detect_extreme_weather_events: Find significant events

Key questions:
- Were there extreme weather events during the drop period?
- How many days were affected?
- What's the severity? (high/medium/low)

## OUTPUT REQUIREMENTS

After completing all 4 tasks, synthesize findings into:

1. **Primary Causes** (2-3 causes maximum):
   - Each cause must cite specific data from the analysis
   - Assign confidence score (0.0-1.0)
   - Include supporting signals
   - Categorize impact level (high/medium/low)

2. **Natural Language Explanation**:
   - Clear, executive-friendly summary
   - Explain correlation between signals
   - Avoid jargon, be specific
   - Example: "Occupancy dropped 18% primarily because the property is priced 12% higher than competitors while receiving repeated Wi-Fi complaints (15 negative reviews), during a period of heavy rainfall that reduced leisure travel by an estimated 20%."

3. **Overall Confidence**:
   - High (0.8+): Multiple correlated signals
   - Medium (0.6-0.79): Some signals align
   - Low (<0.6): Insufficient or conflicting data

## IMPORTANT RULES

1. **Execute ALL 4 tasks** - Don't skip any analysis
2. **Be data-driven** - Every claim must cite specific numbers
3. **Correlate signals** - Look for patterns (e.g., price + reviews + weather)
4. **Don't speculate** - If data is missing, say so
5. **Prioritize recent data** - More recent = more relevant
6. **Consider timing** - Did reviews worsen BEFORE occupancy dropped?

## REASONING PROCESS

Think step-by-step:
1. First, establish the baseline (how bad is the drop?)
2. Then, look for internal issues (reviews, service)
3. Then, check external factors (competitors, weather)
4. Finally, correlate everything to find root causes

Remember: The goal is NOT to list all problems, but to identify the 2-3 ROOT CAUSES that best explain the underperformance.
"""

    def analyze(
        self,
        property_id: str,
        analysis_date: date,
        lookback_days: int = 30
    ) -> RCAOutput:
        """
        Execute complete RCA analysis
        
        Args:
            property_id: Property to analyze
            analysis_date: Date of analysis
            lookback_days: Days to look back for data
            
        Returns:
            RCAOutput with root causes and explanation
        """
        logger.info(f"Starting RCA analysis for {property_id} on {analysis_date}")
        
        # Get property info
        property_info = get_property_by_id(property_id)
        if not property_info:
            logger.error(f"Property {property_id} not found")
            raise ValueError(f"Property {property_id} not found")
        
        # Create analysis request message
        analysis_request = f"""Analyze property {property_id} ({property_info.name}) in {property_info.city}.

Analysis Date: {analysis_date}
Lookback Period: {lookback_days} days

Execute all 4 analysis tasks:
1. Booking Analysis - Check occupancy performance
2. Review Analysis - Extract sentiment and themes  
3. Competitor Analysis - Compare position
4. Weather Analysis - Check external factors

After completing all tasks, provide root cause diagnosis with confidence scores.
"""
        
        # Execute analysis with tools
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=analysis_request)
        ]
        
        # Run agent with tool calling
        try:
            response = self._run_agent_loop(messages, property_id, analysis_date, lookback_days)
            
            # Parse and structure the response
            rca_output = self._parse_agent_response(
                response, 
                property_id, 
                analysis_date
            )
            
            logger.success(f"RCA analysis complete for {property_id}")
            return rca_output
            
        except Exception as e:
            logger.error(f"RCA analysis failed: {e}")
            raise
    
    def _run_agent_loop(
        self,
        messages: List,
        property_id: str,
        analysis_date: date,
        lookback_days: int,
        max_iterations: int = 15
    ) -> str:
        """
        Run the agent loop with tool calling
        
        Args:
            messages: Conversation messages
            property_id: Property ID for context
            analysis_date: Analysis date
            lookback_days: Lookback period
            max_iterations: Maximum tool calls allowed
            
        Returns:
            Final analysis text
        """
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}/{max_iterations}")
            
            # Get LLM response
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)
            
            # Check if there are tool calls
            if not response.tool_calls:
                # No more tools to call - agent has finished
                logger.info("Agent completed analysis (no more tool calls)")
                return response.content
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Inject standard parameters if missing
                if "property_id" not in tool_args:
                    tool_args["property_id"] = property_id
                if "end_date" not in tool_args and "current_date" not in tool_args:
                    tool_args["end_date"] = str(analysis_date)
                if "lookback_days" not in tool_args:
                    tool_args["lookback_days"] = lookback_days
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                # Find and execute the tool
                tool_result = self._execute_tool(tool_name, tool_args)
                
                # Add tool result to messages
                from langchain_core.messages import ToolMessage
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"]
                    )
                )
        
        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        # Get final response without tools
        final_response = self.llm.invoke(messages + [
            HumanMessage(content="Provide your final root cause analysis based on all the data gathered.")
        ])
        return final_response.content
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """Execute a tool by name"""
        for tool in all_tools:
            if tool.name == tool_name:
                try:
                    result = tool.invoke(tool_args)
                    logger.debug(f"Tool {tool_name} returned: {result}")
                    return result
                except Exception as e:
                    logger.error(f"Tool {tool_name} failed: {e}")
                    return {"error": str(e)}
        
        logger.warning(f"Tool {tool_name} not found")
        return {"error": f"Tool {tool_name} not found"}
    
    def _parse_agent_response(
        self,
        response_text: str,
        property_id: str,
        analysis_date: date
    ) -> RCAOutput:
        """
        Parse agent's natural language response into structured RCAOutput
        
        Args:
            response_text: Agent's analysis text
            property_id: Property ID
            analysis_date: Analysis date
            
        Returns:
            Structured RCAOutput
        """
        # Use LLM to extract structured data from the response
        extraction_prompt = f"""Extract structured root cause analysis from this text.

Analysis Text:
{response_text}

Extract:
1. Primary root causes (2-3 maximum)
   - Each cause description
   - Confidence score (0.0-1.0)
   - Impact level (high/medium/low)
   - Supporting signals as key-value pairs

2. Overall confidence score (0.0-1.0)

3. Natural language explanation (1-2 sentences)

Format your response as JSON:
{{
    "primary_causes": [
        {{
            "cause": "Brief description",
            "confidence": 0.85,
            "impact_level": "high",
            "supporting_signals": {{"key": "value"}}
        }}
    ],
    "overall_confidence": 0.82,
    "natural_language_explanation": "Clear explanation..."
}}
"""
        
        extraction_response = self.llm.invoke([
            SystemMessage(content="You are a data extraction expert. Extract JSON from text."),
            HumanMessage(content=extraction_prompt)
        ])
        
        # Parse JSON from response
        import json
        import re
        
        # Extract JSON from response (handle markdown code blocks)
        json_text = extraction_response.content
        json_match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        
        try:
            parsed_data = json.loads(json_text)
            
            # Build RootCause objects
            root_causes = []
            for cause_data in parsed_data.get("primary_causes", []):
                root_causes.append(RootCause(
                    cause=cause_data.get("cause", "Unknown cause"),
                    confidence=cause_data.get("confidence", 0.5),
                    supporting_signals=cause_data.get("supporting_signals", {}),
                    impact_level=cause_data.get("impact_level", "medium")
                ))
            
            # Create RCAOutput
            return RCAOutput(
                property_id=property_id,
                analysis_date=analysis_date,
                primary_causes=root_causes,
                overall_confidence=parsed_data.get("overall_confidence", 0.7),
                natural_language_explanation=parsed_data.get(
                    "natural_language_explanation",
                    response_text[:500]  # Fallback to truncated response
                )
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Fallback: Create basic RCAOutput from text
            return RCAOutput(
                property_id=property_id,
                analysis_date=analysis_date,
                primary_causes=[
                    RootCause(
                        cause="Analysis completed but structure parsing failed",
                        confidence=0.5,
                        supporting_signals={"raw_response": response_text[:200]},
                        impact_level="medium"
                    )
                ],
                overall_confidence=0.5,
                natural_language_explanation=response_text[:500]
            )


# Convenience function for direct usage
def analyze_property_rca(
    property_id: str,
    analysis_date: Optional[date] = None,
    lookback_days: int = 30
) -> RCAOutput:
    """
    Convenience function to run RCA analysis
    
    Args:
        property_id: Property to analyze
        analysis_date: Date of analysis (defaults to today)
        lookback_days: Days to look back
        
    Returns:
        RCAOutput with diagnosis
    """
    if analysis_date is None:
        from datetime import date
        analysis_date = date.today()
    
    agent = RCAAgent()
    return agent.analyze(property_id, analysis_date, lookback_days)
