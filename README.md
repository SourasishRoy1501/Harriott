# Harriot Smart Occupancy Agent (SOA)

An AI-driven diagnostic and decision engine that explains why properties are underperforming and prescribes segment-specific actions.

## Project Overview

SOA Phase 1 focuses on:
- **Root Cause Analysis (RCA)**: Multi-signal correlation to identify underperformance drivers
- **Customer Segmentation**: Age-based segmentation for targeted strategies
- **Action Strategy**: Prescriptive recommendations based on RCA + segment insights

## Tech Stack

- **Python 3.11+**
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM integration and tooling
- **Supabase**: PostgreSQL database with real-time capabilities
- **OpenAI GPT-4**: LLM for analysis and reasoning

## Project Structure

```
harriot-soa/
├── src/
│   ├── agents/              # LangGraph agent implementations
│   │   ├── rca_agent.py     # Root Cause Analysis Agent
│   │   ├── segmentation_agent.py
│   │   └── action_strategy_agent.py
│   ├── tools/               # LangChain tools for data access
│   │   ├── booking_tools.py
│   │   ├── review_tools.py
│   │   ├── weather_tools.py
│   │   └── competitor_tools.py
│   ├── graphs/              # LangGraph workflow definitions
│   │   └── soa_workflow.py
│   ├── database/            # Database connection and queries
│   │   ├── supabase_client.py
│   │   └── queries.py
│   ├── models/              # Pydantic models for data validation
│   │   └── schemas.py
│   └── utils/               # Helper functions
│       ├── nlp_helpers.py
│       └── date_helpers.py
├── tests/
├── config/
│   └── settings.py
├── notebooks/               # Exploratory analysis
├── .env.example
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - OPENAI_API_KEY
```

### 3. Verify Database Connection

```bash
python -c "from src.database.supabase_client import get_supabase_client; print('Connected!' if get_supabase_client() else 'Failed')"
```

## Quick Start

```python
from src.graphs.soa_workflow import create_soa_workflow

# Initialize workflow
workflow = create_soa_workflow()

# Run analysis for a property
result = workflow.invoke({
    "property_id": "PROP_001",
    "analysis_date": "2024-01-15"
})

print(result["rca_output"])
print(result["recommended_actions"])
```

## Development Workflow

1. **Add new tools**: Create in `src/tools/` and register with agents
2. **Extend agents**: Modify agent logic in `src/agents/`
3. **Update workflow**: Adjust graph flow in `src/graphs/soa_workflow.py`
4. **Test**: Add tests in `tests/` directory

## Phase 1 Deliverables

- ✅ Multi-signal RCA engine
- ✅ Age-based customer segmentation
- ✅ Action strategy recommendations
- ✅ Human-in-the-loop approval interface
- ✅ Explainable AI outputs with confidence scores

## Future Phases

- Phase 2: GenAI content generation
- Phase 3: Impact estimation & RL learning
- Phase 4: Automated execution pipelines

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## License

Proprietary - Harriot Inc.
