# Harriot SOA - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
python test_connection.py

# Run tools
python -c "from src.tools.booking_tools import *; help(get_occupancy_trends)"
```

## 📁 Key Files Location

| What | Where |
|------|-------|
| Database queries | `src/database/queries.py` |
| All tools | `src/tools/*.py` |
| Data models | `src/models/schemas.py` |
| Config | `config/settings.py` |
| Build agents here → | `src/agents/` |

## 🛠️ Available Tools (13)

### Booking (3)
```python
get_occupancy_trends(property_id, end_date, lookback_days)
analyze_occupancy_drop(property_id, current_date, lookback_days)
check_weekday_weekend_pattern(property_id, end_date, lookback_days)
```

### Reviews (4)
```python
analyze_review_themes(property_id, end_date, lookback_days)
get_negative_review_insights(property_id, end_date, lookback_days)
analyze_review_sentiment_trend(property_id, end_date, lookback_days)
get_rating_distribution(property_id, end_date, lookback_days)
```

### Weather (2)
```python
analyze_weather_impact(property_id, end_date, lookback_days)
detect_extreme_weather_events(property_id, end_date, lookback_days)
```

### Competitors (3)
```python
analyze_competitor_pricing(property_id, end_date, lookback_days)
compare_property_amenities(property_id)
get_competitor_context(property_id)
```

## 🎯 Build Order

1. **RCA Agent** (`src/agents/rca_agent.py`) - Start here!
2. **Segmentation Agent** (`src/agents/segmentation_agent.py`)
3. **Action Strategy Agent** (`src/agents/action_strategy_agent.py`)
4. **Workflow** (`src/graphs/soa_workflow.py`)
5. **API/Dashboard** (your choice)

## 💻 Example: Build RCA Agent

```python
# src/agents/rca_agent.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from src.tools import all_tools
from config.settings import get_settings

settings = get_settings()

rca_agent = create_react_agent(
    model=ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.llm_temperature
    ),
    tools=all_tools,
    state_modifier="""You are a Root Cause Analysis expert for hotel occupancy.

Your goal: Identify WHY a property is underperforming.

Process:
1. Check occupancy trends - has it dropped?
2. Analyze reviews - what are guests saying?
3. Check weather - any travel deterrents?
4. Compare competitors - pricing and amenities

Output format:
- List of root causes (max 3)
- Confidence score for each
- Supporting evidence
- Natural language explanation

Be specific and data-driven."""
)
```

## 🧪 Test an Agent

```python
from src.agents.rca_agent import rca_agent

result = rca_agent.invoke({
    "messages": [{
        "role": "user",
        "content": """Analyze property PROP_001 for date 2024-01-15 
        with 30-day lookback. Why is occupancy down?"""
    }]
})

print(result)
```

## 📊 Database Schema Quick Ref

```sql
properties(id, name, city, category, total_rooms)
booking_trends(property_id, date, occupancy_percentage, bookings, avg_daily_rate)
reviews(property_id, rating, review_text, review_date)
weather_daily(city, date, weather_type, temperature, rainfall_mm)
competitors(property_id, name, distance_km, category)
pricing_daily(competitor_id, date, avg_price)
property_amenities(entity_id, amenity, available)
```

## 🎨 Data Models

```python
# Input
PropertyAnalysisRequest(property_id, analysis_date, lookback_days)

# Agent Outputs
RCAOutput(property_id, primary_causes, confidence, explanation)
CustomerSegmentOutput(dominant_segment, confidence, behavioral_notes)
ActionStrategyOutput(target_segment, recommended_actions)

# Workflow State
SOAWorkflowState(property_id, rca_output, segmentation_output, action_strategy_output)
```

## 🔍 Debugging

```bash
# Enable tracing
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-key

# Check logs
tail -f logs/soa.log

# Test database
python test_connection.py

# Test individual tool
python -c "from src.tools.booking_tools import analyze_occupancy_drop; print(analyze_occupancy_drop.invoke({'property_id': 'PROP_001', 'current_date': '2024-01-15'}))"
```

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| `README.md` | Overview |
| `SETUP.md` | Detailed setup |
| `QUICKSTART.md` | Fast start |
| `PROJECT_OVERVIEW.md` | Architecture |
| `IMPLEMENTATION_SUMMARY.md` | Status |

## ⚡ Pro Tips

1. **Start simple** - Test with one property first
2. **Use LangSmith** - Debug agent behavior
3. **Test tools individually** - Before building agents
4. **Iterate prompts** - Agent quality = prompt quality
5. **Check types** - Pydantic will catch errors early

## 🎯 Success Metrics

- RCA identifies root causes correctly ✓
- Confidence scores are accurate ✓
- Actions are segment-specific ✓
- Workflow completes without errors ✓
- Human can approve/reject ✓

## 📞 Getting Help

1. Read the docs (especially QUICKSTART.md)
2. Check test_connection.py output
3. Enable verbose logging
4. Test components in isolation
5. Review LangSmith traces

---

**Remember**: The foundation is complete. Just add the intelligence! 🧠
