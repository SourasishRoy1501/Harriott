"""
Harriot SOA FastAPI Application

Main FastAPI app with all routes and configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/api.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

# Import routes
from api.routes import dashboard, property, analysis

# Create FastAPI app
app = FastAPI(
    title="Harriot Smart Occupancy Agent API",
    description="""
    AI-powered occupancy analysis and optimization platform for hotels.
    
    ## Features
    
    * **Dashboard**: Portfolio metrics and property feed
    * **Property Details**: Competitor pricing, reviews, amenities, trends, weather
    * **AI Analysis**: Root cause analysis, action recommendations, impact predictions
    
    ## Workflow
    
    1. View dashboard → Select underperforming property
    2. View property details → Charts, reviews, amenities
    3. Click "Analyze" → AI runs complete analysis
    4. View results → RCA + Action cards + Impact forecast
    5. Approve actions → Implement recommendations
    
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(property.router)
app.include_router(analysis.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Harriot Smart Occupancy Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "harriot-soa-api",
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
