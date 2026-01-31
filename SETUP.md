# Harriot SOA - Setup Guide

## Prerequisites

- Python 3.11 or higher
- Supabase account with database access
- OpenAI API key

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Clone the repository (if applicable)
cd harriot-soa

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required variables in `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
OPENAI_API_KEY=sk-your-openai-key
```

### 4. Verify Database Connection

```bash
python test_connection.py
```

Expected output:
```
✓ Settings loaded - Environment: development
✓ Supabase connection successful
✓ Found X properties
✓ Found X days of booking data
✓ All tests completed successfully!
```

### 5. Download NLTK Data (for NLP features)

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Project Structure

```
harriot-soa/
├── config/                 # Configuration
│   └── settings.py        # Settings management
├── src/
│   ├── agents/            # LangGraph agents (to be created)
│   ├── tools/             # LangChain tools for data access
│   │   ├── booking_tools.py
│   │   ├── review_tools.py
│   │   ├── weather_tools.py
│   │   └── competitor_tools.py
│   ├── database/          # Database layer
│   │   ├── supabase_client.py
│   │   └── queries.py
│   ├── models/            # Pydantic models
│   │   └── schemas.py
│   ├── utils/             # Utilities
│   │   ├── nlp_helpers.py
│   │   └── date_helpers.py
│   └── graphs/            # LangGraph workflows (to be created)
├── tests/                 # Test files
├── notebooks/             # Jupyter notebooks for exploration
├── test_connection.py     # Connection test script
└── requirements.txt       # Python dependencies
```

## Next Steps

### Create Agents

The following agents need to be implemented:

1. **RCA Agent** (`src/agents/rca_agent.py`)
   - Orchestrates all tools
   - Correlates signals
   - Generates root cause analysis

2. **Segmentation Agent** (`src/agents/segmentation_agent.py`)
   - Analyzes customer demographics
   - Identifies dominant age segment

3. **Action Strategy Agent** (`src/agents/action_strategy_agent.py`)
   - Takes RCA output + segment
   - Generates actionable recommendations

### Create LangGraph Workflow

Create `src/graphs/soa_workflow.py`:
- Define workflow state
- Connect agents in sequence
- Add decision nodes
- Implement human-in-the-loop

### Testing Tools

You can test individual tools:

```python
from src.tools.booking_tools import get_occupancy_trends
from datetime import date

result = get_occupancy_trends(
    property_id="PROP_001",
    end_date="2024-01-15",
    lookback_days=30
)
print(result)
```

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Verify `.env` file exists and has correct credentials
2. Check Supabase project is active
3. Verify network access to Supabase

### Import Errors

If you get import errors:
1. Ensure virtual environment is activated
2. Reinstall requirements: `pip install -r requirements.txt`
3. Check Python version: `python --version`

### NLTK Errors

If NLP functions fail:
```python
import nltk
nltk.download('all')  # Download all NLTK data
```

## Development Workflow

1. Create a new branch for features
2. Write tests for new functionality
3. Run tests: `pytest tests/`
4. Format code: `black src/`
5. Lint code: `ruff src/`

## Useful Commands

```bash
# Run connection test
python test_connection.py

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Run tests
pytest tests/ -v

# Type checking
mypy src/
```

## Support

For issues or questions:
1. Check this setup guide
2. Review error logs
3. Contact the development team
