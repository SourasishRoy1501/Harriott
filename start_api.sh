#!/bin/bash

# Harriot SOA API Startup Script

echo "🚀 Starting Harriot SOA API..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Create logs directory if doesn't exist
mkdir -p logs

# Start the API server
echo "🌐 Starting FastAPI server on http://localhost:3000"
echo "📚 API Documentation: http://localhost:3000/docs"
echo "📖 ReDoc: http://localhost:3000/redoc"
echo ""

python -m uvicorn api.main:app --host 0.0.0.0 --port 3001 --reload
