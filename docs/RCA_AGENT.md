# RCA Agent - Documentation

## Overview

The **Root Cause Analysis (RCA) Agent** is the diagnostic brain of the Harriot Smart Occupancy Agent system. It analyzes property underperformance by executing 4 core analysis tasks and correlating multiple data signals.

## Core Architecture

### 4 Analysis Tasks

The RCA Agent executes these tasks **sequentially**:

#### 1. 📊 Booking Analysis
**Goal**: Determine if property is over/underperforming

**Tools Used**:
- `get_occupancy_trends` - Overall patterns
- `analyze_occupancy_drop` - Quantify decline
- `check_weekday_weekend_pattern` - Identify specific issues

**Output**: Occupancy trend, drop percentage, pattern type

---

#### 2. 💬 Review Analysis  
**Goal**: Extract guest sentiment and identify specific problems

**Tools Used**:
- `analyze_review_themes` - Top themes with sentiment
- `get_negative_review_insights` - Focus on complaints
- `analyze_review_sentiment_trend` - Track changes
- `get_rating_distribution` - Rating patterns

**Output**: Review themes, sentiment scores, complaint patterns

---

#### 3. 🏨 Competitor Analysis
**Goal**: Understand competitive positioning

**Tools Used**:
- `analyze_competitor_pricing` - Price gap
- `compare_property_amenities` - Feature gaps
- `get_competitor_context` - Competitive pressure

**Output**: Price positioning, amenity gaps, competitive landscape

---

#### 4. 🌤️ Weather Analysis
**Goal**: Detect external travel deterrents

**Tools Used**:
- `analyze_weather_impact` - Overall impact assessment
- `detect_extreme_weather_events` - Significant events

**Output**: Weather events, severity, travel impact

---

## How It Works

### Agent Loop Flow

```
Start
  ↓
[System Prompt] → Define RCA mission and framework
  ↓
[User Request] → "Analyze property PROP_001"
  ↓
[Agent Loop - Iteration 1-15]
  ↓
Agent selects tool → get_occupancy_trends
  ↓
Tool executes → Returns occupancy data
  ↓
Agent reasons → "Drop detected, need reviews"
  ↓
Agent selects tool → analyze_review_themes
  ↓
Tool executes → Returns review themes
  ↓
Agent reasons → "Wi-Fi complaints, check competitors"
  ↓
Agent selects tool → analyze_competitor_pricing
  ↓
... continues until all 4 tasks complete ...
  ↓
Agent provides final diagnosis
  ↓
[Parse Response] → Extract structured data
  ↓
Return RCAOutput
```

### Correlation Logic

The agent **correlates signals** across all 4 analyses:

**Example Correlation**:
```
Booking: 18% occupancy drop
Review: Wi-Fi complaints (15 negative mentions)
Competitor: 12% price premium
Weather: Heavy rain (8 days)

Agent reasoning:
"Property is underperforming due to PRICE+QUALITY gap during unfavorable weather"

Root Cause: 
- Premium pricing without matching quality
- Wi-Fi issues deterring work travelers
- Rain reducing leisure demand
```

---

## Usage

### Basic Usage

```python
from src.agents.rca_agent import analyze_property_rca
from datetime import date

result = analyze_property_rca(
    property_id="PROP_001",
    analysis_date=date(2024, 1, 15),
    lookback_days=30
)

print(result.natural_language_explanation)
for cause in result.primary_causes:
    print(f"- {cause.cause} (confidence: {cause.confidence})")
```

### Advanced Usage with Agent Class

```python
from src.agents.rca_agent import RCAAgent
from datetime import date

# Initialize agent
agent = RCAAgent()

# Run analysis
result = agent.analyze(
    property_id="PROP_001",
    analysis_date=date(2024, 1, 15),
    lookback_days=30
)

# Access detailed results
for cause in result.primary_causes:
    print(f"Cause: {cause.cause}")
    print(f"Confidence: {cause.confidence}")
    print(f"Impact: {cause.impact_level}")
    print(f"Signals: {cause.supporting_signals}")
```

### Integration with Workflow

```python
from src.agents.rca_agent import RCAAgent
from src.models.schemas import SOAWorkflowState

def rca_node(state: SOAWorkflowState) -> SOAWorkflowState:
    """LangGraph node for RCA analysis"""
    agent = RCAAgent()
    
    rca_output = agent.analyze(
        property_id=state.property_id,
        analysis_date=state.analysis_date,
        lookback_days=state.lookback_days
    )
    
    state.rca_output = rca_output
    return state
```

---

## Output Structure

### RCAOutput Model

```python
RCAOutput(
    property_id: str,                          # "PROP_001"
    analysis_date: date,                       # Date of analysis
    primary_causes: List[RootCause],          # 2-3 root causes
    overall_confidence: float,                 # 0.0-1.0
    natural_language_explanation: str          # Executive summary
)
```

### RootCause Model

```python
RootCause(
    cause: str,                               # "Price 12% above competitors"
    confidence: float,                        # 0.85
    supporting_signals: Dict[str, Any],       # {"price_gap": "12%", "reviews": 15}
    impact_level: str                         # "high" | "medium" | "low"
)
```

---

## Configuration

### Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o           # or gpt-4o-mini
LLM_TEMPERATURE=0.2           # Lower = more deterministic
```

### Agent Settings

Edit `config/settings.py`:

```python
class Settings(BaseSettings):
    openai_model: str = "gpt-4o"
    llm_temperature: float = 0.2
    confidence_threshold: float = 0.70
```

---

## Customization

### Modify System Prompt

Edit `src/agents/rca_agent.py`:

```python
self.system_prompt = """Your custom prompt here..."""
```

### Add Custom Analysis Task

```python
# In system_prompt, add Task 5:
### Task 5: LOCAL EVENTS ANALYSIS
Goal: Check for local events affecting travel
Tools to use:
- your_custom_tool

# The agent will automatically include this in analysis
```

### Adjust Tool Parameters

```python
def _run_agent_loop(self, ...):
    # Modify default parameters
    if "lookback_days" not in tool_args:
        tool_args["lookback_days"] = 45  # Longer lookback
```

---

## Debugging

### Enable Detailed Logging

```python
from loguru import logger

logger.add(
    "logs/rca_agent.log",
    level="DEBUG",
    rotation="1 day"
)
```

### Enable LangSmith Tracing

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-key
export LANGCHAIN_PROJECT=harriot-rca
```

View traces at: https://smith.langchain.com

### Inspect Tool Calls

```python
# Add to _execute_tool method:
logger.info(f"Tool: {tool_name}")
logger.info(f"Args: {tool_args}")
logger.info(f"Result: {result}")
```

---

## Performance

### Typical Analysis Time

- **Small property** (30 days data): 10-20 seconds
- **Large property** (90 days data): 30-45 seconds
- **Multiple properties**: ~20 seconds each

### Cost Estimate (OpenAI)

- **GPT-4o**: ~$0.05-0.10 per analysis
- **GPT-4o-mini**: ~$0.01-0.02 per analysis

### Optimization Tips

1. **Use gpt-4o-mini** for faster/cheaper results
2. **Reduce lookback_days** for faster analysis
3. **Cache tool results** if analyzing same property multiple times
4. **Batch analyses** in parallel

---

## Error Handling

### Common Errors

**1. Property Not Found**
```python
# Error: Property PROP_XXX not found
# Solution: Verify property_id exists in database
from src.database.queries import get_all_properties
properties = get_all_properties()
```

**2. No Data Available**
```python
# Error: No booking data available
# Solution: Check date range has data
# The agent will note this in low confidence
```

**3. Tool Execution Failed**
```python
# Error: Tool analyze_occupancy_drop failed
# Solution: Check database connection, verify data exists
```

### Graceful Degradation

The agent handles missing data gracefully:

```python
# If reviews missing:
"Review analysis unavailable - no recent reviews found"

# If weather data missing:
"Weather impact could not be assessed - no data for {city}"

# Agent still provides analysis with available data
```

---

## Testing

### Run Test Suite

```bash
python test_rca_agent.py
```

### Manual Testing

```python
from src.agents.rca_agent import analyze_property_rca
from datetime import date

# Test with known property
result = analyze_property_rca("PROP_001", date(2024, 1, 15), 30)

# Verify output
assert result.property_id == "PROP_001"
assert 0 <= result.overall_confidence <= 1
assert len(result.primary_causes) <= 3
```

### Integration Testing

```python
def test_rca_with_mock_data():
    # Setup mock data
    # Run agent
    # Verify expected causes
    pass
```

---

## Examples

### Example 1: Simple Analysis

```python
result = analyze_property_rca("PROP_001", date.today(), 30)
print(result.natural_language_explanation)
```

Output:
```
"Occupancy dropped 18% primarily because the property is priced 12% 
higher than competitors while receiving repeated Wi-Fi complaints 
(15 negative reviews), during a period of heavy rainfall that reduced 
leisure travel."
```

### Example 2: Multiple Properties Comparison

```python
from src.database.queries import get_all_properties

properties = get_all_properties()
results = {}

for prop in properties:
    result = analyze_property_rca(prop.id, date.today(), 30)
    results[prop.name] = result.overall_confidence

# Find lowest confidence (most problematic)
worst_property = min(results, key=results.get)
print(f"Most concerning: {worst_property}")
```

### Example 3: Time Series Analysis

```python
from datetime import timedelta

dates = [date.today() - timedelta(days=i*7) for i in range(4)]
trends = []

for analysis_date in dates:
    result = analyze_property_rca("PROP_001", analysis_date, 7)
    trends.append({
        "date": analysis_date,
        "confidence": result.overall_confidence,
        "top_cause": result.primary_causes[0].cause
    })

# Track how issues evolved
for trend in trends:
    print(f"{trend['date']}: {trend['top_cause']}")
```

---

## Best Practices

### 1. Use Appropriate Lookback Periods

```python
# Recent issues: 7-14 days
analyze_property_rca(prop_id, date.today(), lookback_days=7)

# Trend analysis: 30 days (default)
analyze_property_rca(prop_id, date.today(), lookback_days=30)

# Seasonal patterns: 90 days
analyze_property_rca(prop_id, date.today(), lookback_days=90)
```

### 2. Check Confidence Scores

```python
result = analyze_property_rca(prop_id, date.today(), 30)

if result.overall_confidence > 0.8:
    print("High confidence - act on recommendations")
elif result.overall_confidence > 0.6:
    print("Medium confidence - investigate further")
else:
    print("Low confidence - collect more data")
```

### 3. Focus on High-Impact Causes

```python
high_impact_causes = [
    cause for cause in result.primary_causes
    if cause.impact_level == "high"
]

# Prioritize these for action
```

### 4. Correlate with Business Context

```python
# Consider seasonality
if is_peak_season(analysis_date):
    # Drop is more concerning
    
# Consider property type
if property.category == "business":
    # Focus on weekday patterns
```

---

## Roadmap

### Current Version (v1.0)
- ✅ 4 core analysis tasks
- ✅ Tool orchestration
- ✅ Correlation logic
- ✅ Structured output

### Planned Enhancements (v1.1)
- 🚧 Custom analysis tasks
- 🚧 Historical comparison
- 🚧 Trend prediction
- 🚧 Multi-property batch analysis

### Future (v2.0)
- 📅 Real-time monitoring
- 📅 Automated alerts
- 📅 Action execution
- 📅 Impact tracking

---

## FAQ

**Q: How long does analysis take?**
A: Typically 10-30 seconds depending on data volume.

**Q: Can I customize the analysis tasks?**
A: Yes, edit the system_prompt in `rca_agent.py`.

**Q: What if data is missing?**
A: Agent handles gracefully, notes in explanation, confidence adjusted.

**Q: How accurate is the diagnosis?**
A: Depends on data quality. Check confidence scores.

**Q: Can I add custom tools?**
A: Yes, create tool in `src/tools/` and add to `all_tools`.

**Q: How do I interpret confidence scores?**
- **0.8+**: High confidence, clear signals
- **0.6-0.79**: Medium, some ambiguity
- **<0.6**: Low, insufficient data

---

## Support

**Documentation**: See `QUICKSTART.md` and `PROJECT_OVERVIEW.md`
**Examples**: `example_rca.py` and `test_rca_agent.py`
**Logs**: Check `logs/rca_agent.log`
**Debugging**: Enable LangSmith tracing

---

**The RCA Agent is production-ready!** 🚀

Start analyzing properties and identifying root causes with confidence.
