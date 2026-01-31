# Harriot Smart Occupancy Agent - Project Overview

## 🎯 Project Mission

Build an AI-driven diagnostic engine that explains **WHY** hotel properties underperform and prescribes targeted actions for specific customer segments.

---

## 📦 What's Been Built (Phase 1 Foundation)

### ✅ Complete Infrastructure (100%)

#### 1. **Configuration & Settings**
- Environment-based configuration with Pydantic
- `.env` support for credentials
- Centralized settings management
- Location: `config/settings.py`

#### 2. **Database Layer** 
- Supabase client connection (singleton pattern)
- 15+ query functions covering:
  - Property management
  - Booking trends & occupancy analysis
  - Review retrieval & filtering
  - Weather data access
  - Competitor analysis
  - Amenity comparison
- Location: `src/database/`

#### 3. **Data Models**
- Complete Pydantic schemas for:
  - Property, Booking, Review entities
  - Weather, Competitor data
  - Agent outputs (RCA, Segmentation, Actions)
  - Workflow state management
- Type-safe, validated data structures
- Location: `src/models/schemas.py`

#### 4. **LangChain Tools** (13 Tools)
Four categories of tools for agent use:

**Booking Tools** (3):
- `get_occupancy_trends` - Analyze occupancy patterns
- `analyze_occupancy_drop` - Detect and quantify drops
- `check_weekday_weekend_pattern` - Identify stay patterns

**Review Tools** (4):
- `analyze_review_themes` - Extract themes with sentiment
- `get_negative_review_insights` - Surface complaints
- `analyze_review_sentiment_trend` - Track changes over time
- `get_rating_distribution` - Understand rating patterns

**Weather Tools** (2):
- `analyze_weather_impact` - Assess travel deterrence
- `detect_extreme_weather_events` - Identify significant events

**Competitor Tools** (3):
- `analyze_competitor_pricing` - Price gap analysis
- `compare_property_amenities` - Identify feature gaps
- `get_competitor_context` - Competitive landscape

Location: `src/tools/`

#### 5. **Utilities**
- **NLP Helpers**: Sentiment analysis, theme extraction, TF-IDF
- **Date Helpers**: Date range calculations, season detection
- Location: `src/utils/`

#### 6. **Documentation**
- `README.md` - Project overview
- `SETUP.md` - Detailed setup instructions
- `QUICKSTART.md` - Fast onboarding guide
- Test script for verification

---

## 🚧 What Needs to Be Built (Phase 1 - Remaining)

### 1. **RCA Agent** (Priority 1) 🔴
**File**: `src/agents/rca_agent.py`

**Purpose**: The diagnostic brain that correlates all signals

**Implementation**:
```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from src.tools import all_tools

rca_agent = create_react_agent(
    model=ChatOpenAI(model="gpt-4o"),
    tools=all_tools,
    state_modifier="""Root Cause Analysis expert for hotels.
    
    Use tools to:
    1. Check occupancy trends
    2. Analyze reviews
    3. Assess weather
    4. Compare competitors
    
    Output: Clear causes with confidence scores"""
)
```

**Key Requirements**:
- Use ALL 13 tools intelligently
- Correlate booking drops with review themes
- Detect weather impact timing
- Compare pricing vs occupancy
- Generate `RCAOutput` with confidence
- Provide natural language explanation

### 2. **Segmentation Agent** (Priority 2) 🟡
**File**: `src/agents/segmentation_agent.py`

**Purpose**: Identify dominant customer age segment

**Implementation**:
- Query customer data from bookings
- Analyze review language for age indicators
- Output `CustomerSegmentOutput` with confidence
- Behavioral notes for segment

**Segments**:
- 18-25: Budget/student
- 26-35: Young professional
- 36-50: Family/business
- 50+: Leisure/comfort

### 3. **Action Strategy Agent** (Priority 3) 🟢
**File**: `src/agents/action_strategy_agent.py`

**Purpose**: Translate diagnosis → actions

**Inputs**: 
- RCA causes
- Customer segment
- Property context

**Output**: 
- Prioritized actions
- Segment-specific tactics
- Implementation complexity
- Expected impact

**Action Types**:
- Pricing adjustments
- Marketing campaigns
- Experience improvements
- Amenity upgrades

### 4. **LangGraph Workflow** (Priority 4) 🔵
**File**: `src/graphs/soa_workflow.py`

**Purpose**: Orchestrate all agents in sequence

**Flow**:
```
Start
  ↓
Fetch Property Data
  ↓
RCA Agent (diagnose)
  ↓
Segmentation Agent (identify customers)
  ↓
Action Strategy Agent (prescribe)
  ↓
Human Approval Gate
  ↓
End (return results)
```

**Features**:
- State management with `SOAWorkflowState`
- Error handling at each step
- Conditional edges (skip if no data)
- Human-in-the-loop approval
- Logging and observability

### 5. **API/Interface Layer** (Priority 5) 🟣
**Options**:
- FastAPI REST endpoints
- Streamlit dashboard
- Gradio interface
- CLI tool

**Endpoints**:
- `POST /analyze` - Run full analysis
- `GET /properties` - List properties
- `GET /analysis/{id}` - Get results
- `POST /approve/{id}` - Approve actions

---

## 🏗️ Project Structure

```
harriot-soa/
├── config/
│   ├── __init__.py
│   └── settings.py              ✅ Settings management
│
├── src/
│   ├── __init__.py
│   │
│   ├── agents/                  🚧 TO BUILD
│   │   ├── __init__.py
│   │   ├── rca_agent.py        ← Build this first
│   │   ├── segmentation_agent.py
│   │   └── action_strategy_agent.py
│   │
│   ├── graphs/                  🚧 TO BUILD
│   │   ├── __init__.py
│   │   └── soa_workflow.py     ← Build after agents
│   │
│   ├── database/                ✅ COMPLETE
│   │   ├── __init__.py
│   │   ├── supabase_client.py
│   │   └── queries.py
│   │
│   ├── tools/                   ✅ COMPLETE
│   │   ├── __init__.py
│   │   ├── booking_tools.py     (3 tools)
│   │   ├── review_tools.py      (4 tools)
│   │   ├── weather_tools.py     (2 tools)
│   │   └── competitor_tools.py  (3 tools)
│   │
│   ├── models/                  ✅ COMPLETE
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   └── utils/                   ✅ COMPLETE
│       ├── __init__.py
│       ├── nlp_helpers.py
│       └── date_helpers.py
│
├── tests/                       🚧 TO BUILD
│   ├── __init__.py
│   ├── agents/
│   └── tools/
│
├── notebooks/                   📓 For exploration
│
├── .env.example                 ✅ Template
├── .gitignore                   ✅ Complete
├── requirements.txt             ✅ All dependencies
├── README.md                    ✅ Overview
├── SETUP.md                     ✅ Setup guide
├── QUICKSTART.md                ✅ Fast start
└── test_connection.py           ✅ Verification script
```

---

## 🎯 Recommended Development Order

### Week 1: Core Agents
1. **Day 1-2**: RCA Agent
   - Start with simple version
   - Test with one property
   - Iterate on prompts
   
2. **Day 3**: Segmentation Agent
   - Query customer data
   - Age classification logic
   
3. **Day 4**: Action Strategy Agent
   - Rule-based initially
   - Segment-specific tactics

### Week 2: Integration
4. **Day 5-6**: LangGraph Workflow
   - Connect agents
   - State management
   - Error handling
   
5. **Day 7**: Testing & Refinement
   - Test with multiple properties
   - Refine prompts
   - Add logging

### Week 3: Interface
6. **Day 8-10**: API/Dashboard
   - Choose framework
   - Build endpoints
   - Basic UI

---

## 📊 Database Schema Reference

Your Supabase has these tables with mock data:

- `properties` - Property details
- `booking_trends` - Daily occupancy & rates
- `reviews` - Guest feedback
- `weather_daily` - Weather conditions
- `competitors` - Competitor listings
- `pricing_daily` - Competitor pricing
- `property_amenities` - Feature availability
- `customers` - Customer demographics

All queries are ready in `src/database/queries.py`

---

## 🚀 Getting Started NOW

1. **Setup** (5 min):
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with credentials
   python test_connection.py
   ```

2. **Test a Tool** (2 min):
   ```python
   from src.tools.booking_tools import analyze_occupancy_drop
   
   result = analyze_occupancy_drop.invoke({
       "property_id": "PROP_001",
       "current_date": "2024-01-15",
       "lookback_days": 30
   })
   print(result)
   ```

3. **Build RCA Agent** (Start here):
   - Open `src/agents/rca_agent.py`
   - Import tools and LangGraph
   - Define agent with system prompt
   - Test with one property

---

## 🎓 Key Concepts

### LangGraph Agent Flow
```
User Request → Agent → Tool Selection → Tool Execution → 
Agent Reasoning → More Tools? → Final Answer
```

### RCA Logic
```
Booking Drop Detected
  ↓
Check Reviews → Wi-Fi complaints
Check Weather → Heavy rain
Check Pricing → 12% premium
  ↓
Correlate: Price + Issues + Weather = Root Causes
```

### State Management
```python
class SOAWorkflowState:
    property_id: str
    rca_output: Optional[RCAOutput]
    segmentation_output: Optional[CustomerSegmentOutput]
    action_strategy_output: Optional[ActionStrategyOutput]
```

---

## 🐛 Debugging Tips

1. **Enable LangSmith** for agent tracing:
   ```bash
   LANGCHAIN_TRACING_V2=true
   ```

2. **Check logs** - Everything is logged with loguru

3. **Test tools independently** before building agents

4. **Start simple** - Single property, simple prompts

---

## 📚 Resources

- [LangGraph Tutorial](https://python.langchain.com/docs/langgraph)
- [LangChain Tools Guide](https://python.langchain.com/docs/modules/tools/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Supabase Python Client](https://supabase.com/docs/reference/python)

---

## ✨ Summary

**What's Done**: 
- All infrastructure ✅
- All tools ✅
- All utilities ✅
- All data models ✅

**What's Next**: 
- Build 3 agents 🔴
- Create workflow 🔵
- Add interface 🟣

**Time Estimate**: 2-3 weeks for complete Phase 1

The foundation is rock-solid. Now build the intelligence layer! 🚀
