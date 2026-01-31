# Quick Start Guide - Harriot SOA

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies (2 min)

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment (1 min)

```bash
# Copy and edit .env file
cp .env.example .env
nano .env
```

Add your credentials:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
OPENAI_API_KEY=sk-...
```

### 3. Test Connection (1 min)

```bash
python test_connection.py
```

Expected: ✓ All tests pass

### 4. Explore the Tools (1 min)

```python
from src.tools.booking_tools import get_occupancy_trends
from datetime import date

# Get occupancy data
result = get_occupancy_trends.invoke({
    "property_id": "PROP_001",
    "end_date": "2024-01-15",
    "lookback_days": 30
})

print(result)
```

## 📋 What's Built So Far

### ✅ Complete
- **Database Layer**: Supabase client + 15+ query functions
- **LangChain Tools**: 13 tools across 4 categories
  - 3 booking/occupancy tools
  - 4 review analysis tools
  - 2 weather analysis tools
  - 3 competitor analysis tools
  - 1 amenity comparison tool
- **Data Models**: Pydantic schemas for type safety
- **NLP Utilities**: Sentiment analysis, theme extraction
- **Configuration**: Settings management with .env

### 🚧 To Build Next (Your Task)

1. **RCA Agent** - The brain of the system
2. **Segmentation Agent** - Customer analysis
3. **Action Strategy Agent** - Recommendations
4. **LangGraph Workflow** - Orchestration
5. **Dashboard/API** - User interface

## 🛠️ Next Steps: Building the RCA Agent

The RCA Agent is the core - it uses all the tools to diagnose underperformance.

### Agent Architecture

```python
# src/agents/rca_agent.py

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from src.tools import all_tools

# Create agent with all tools
rca_agent = create_react_agent(
    model=ChatOpenAI(model="gpt-4o", temperature=0.2),
    tools=all_tools,
    state_modifier="""You are a Root Cause Analysis expert for hotel occupancy.

Your goal: Identify WHY a property is underperforming by:
1. Analyzing booking trends
2. Reviewing guest feedback
3. Checking weather impact
4. Comparing with competitors

Provide clear, explainable causes with confidence scores."""
)
```

### Example Agent Flow

```
Input: Property PROP_001, Date: 2024-01-15

↓ Agent uses tools:
1. get_occupancy_trends() → "30% drop detected"
2. analyze_occupancy_drop() → "Significant decline in period 2"
3. analyze_review_themes() → "Wi-Fi complaints trending"
4. get_negative_review_insights() → "5 Wi-Fi mentions in bad reviews"
5. analyze_weather_impact() → "Heavy rainfall: 8 days"
6. analyze_competitor_pricing() → "12% more expensive"

↓ Agent synthesizes:
ROOT CAUSES:
1. Price gap (12% premium) + Wi-Fi issues
2. Heavy rainfall reduced travel
3. Competitor advantage on value

↓ Output:
RCAOutput with causes, confidence, explanation
```

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `src/tools/booking_tools.py` | Occupancy & booking analysis |
| `src/tools/review_tools.py` | Sentiment & theme extraction |
| `src/tools/weather_tools.py` | Weather impact detection |
| `src/tools/competitor_tools.py` | Competitive analysis |
| `src/database/queries.py` | All database queries |
| `src/models/schemas.py` | Data models & types |
| `config/settings.py` | Configuration |

## 🎯 Testing Individual Components

### Test a Tool
```python
from src.tools.review_tools import analyze_review_themes

result = analyze_review_themes.invoke({
    "property_id": "PROP_001",
    "end_date": "2024-01-15",
    "lookback_days": 30
})

print(result["top_themes"])
```

### Test Database Query
```python
from src.database.queries import get_reviews
from datetime import date, timedelta

reviews = get_reviews(
    "PROP_001",
    date.today() - timedelta(days=30),
    date.today()
)

print(f"Found {len(reviews)} reviews")
```

### Test NLP
```python
from src.utils.nlp_helpers import extract_themes_from_reviews
from src.database.queries import get_reviews
from datetime import date, timedelta

reviews = get_reviews("PROP_001", date.today() - timedelta(30), date.today())
themes = extract_themes_from_reviews(reviews)

for theme in themes:
    print(f"{theme.theme}: {theme.sentiment_score} ({theme.mention_count} mentions)")
```

## 🔧 Development Tips

1. **Use LangSmith** for debugging agents:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-key
   ```

2. **Test tools individually** before building agents

3. **Check logs** - all operations are logged with loguru

4. **Mock data** - Your Supabase has mock data, use it!

## 🐛 Common Issues

**"Module not found"**
```bash
# Make sure you're in the right directory
cd /path/to/harriot-soa
# Activate venv
source venv/bin/activate
```

**"Supabase connection failed"**
- Check .env file exists
- Verify credentials are correct
- Test with: `python test_connection.py`

**"No data returned"**
- Check property_id exists in database
- Verify date range has data
- Use: `get_all_properties()` to see available properties

## 📖 Learning Resources

- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [Pydantic Models](https://docs.pydantic.dev/)

## 🎉 You're Ready!

The foundation is solid. Now build the agents! Start with the RCA Agent - it's the core intelligence of the system.

**Pro tip**: Begin by writing the RCA agent prompt/instructions, then let it use the tools naturally to diagnose issues.
