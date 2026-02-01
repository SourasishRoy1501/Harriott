## 📚 Harriot SOA API Documentation

Complete REST API documentation for the Harriot Smart Occupancy Agent frontend integration.

---

## 🚀 Quick Start

### Start the API

```bash
# Option 1: Using startup script
./start_api.sh

# Option 2: Direct command
python -m uvicorn api.main:app --host 0.0.0.0 --port 3000 --reload
```

### API will be available at:
- **Base URL**: `http://localhost:3000`
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

---

## 📋 API Endpoints

### 1. Dashboard APIs

#### GET `/api/dashboard/metrics`
Get main dashboard metrics

**Response**:
```json
{
  "avg_occupancy": 72.4,
  "occupancy_change": 4.1,
  "projected_uplift": 8.5,
  "active_agents": 18,
  "pending_approvals": 4
}
```

**Frontend Usage**:
```javascript
// Display in dashboard cards
const metrics = await fetch('/api/dashboard/metrics').then(r => r.json());
document.querySelector('.avg-occupancy').textContent = `${metrics.avg_occupancy}%`;
document.querySelector('.projected-uplift').textContent = `+${metrics.projected_uplift}%`;
```

---

#### GET `/api/dashboard/portfolio`
Get live portfolio feed with all properties

**Response**:
```json
{
  "properties": [
    {
      "property_id": "PROP_001",
      "name": "Grand Harriot Downtown",
      "city": "Seattle, WA",
      "status": "critical",
      "occupancy": 42,
      "revpar": 185,
      "recommendations_count": 3,
      "last_analyzed": "2026-01-29"
    },
    {
      "property_id": "PROP_002",
      "name": "Harriot Seaside Resort",
      "city": "San Diego, CA",
      "status": "healthy",
      "occupancy": 88,
      "revpar": 320,
      "recommendations_count": 0,
      "last_analyzed": null
    }
  ],
  "total_properties": 5,
  "live_connection_status": "stable"
}
```

**Frontend Usage**:
```javascript
// Display in portfolio table
const portfolio = await fetch('/api/dashboard/portfolio').then(r => r.json());

portfolio.properties.forEach(prop => {
  addPropertyRow({
    name: prop.name,
    status: prop.status,  // "critical" | "at_risk" | "healthy"
    occupancy: `${prop.occupancy}%`,
    revpar: `$${prop.revpar}`,
    actions: prop.recommendations_count
  });
});
```

---

### 2. Property Detail APIs

All property endpoints take `property_id` as path parameter and optional `days` query parameter (default: 30).

#### GET `/api/property/{property_id}/competitor-pricing?days=30`
Get competitor pricing comparison chart data

**Response**:
```json
{
  "property_id": "PROP_001",
  "property_name": "Grand Harriot Downtown",
  "period_start": "2026-01-01",
  "period_end": "2026-01-30",
  "pricing_data": [
    {
      "date": "2026-01-01",
      "property_rate": 4500.00,
      "competitor_avg_rate": 3000.00,
      "gap_percentage": 50.00
    },
    // ... more data points
  ],
  "avg_gap_percentage": 49.22,
  "positioning": "premium"
}
```

**Frontend Usage**:
```javascript
// Chart.js or Recharts
const pricing = await fetch(`/api/property/${propertyId}/competitor-pricing?days=30`)
  .then(r => r.json());

const chartData = pricing.pricing_data.map(d => ({
  date: d.date,
  property: d.property_rate,
  competitors: d.competitor_avg_rate
}));

// Show pricing gap indicator
const gapIndicator = document.querySelector('.price-gap');
gapIndicator.textContent = `${pricing.avg_gap_percentage > 0 ? '+' : ''}${pricing.avg_gap_percentage}%`;
gapIndicator.className = pricing.positioning; // "premium" | "competitive" | "budget"
```

---

#### GET `/api/property/{property_id}/reviews?days=30`
Get review statistics

**Response**:
```json
{
  "total_reviews": 20,
  "avg_rating": 2.0,
  "rating_distribution": {
    "1": 6,
    "2": 8,
    "3": 6,
    "4": 0,
    "5": 0
  },
  "recent_reviews": [
    {
      "rating": 2,
      "text": "Internet issues made work difficult...",
      "date": "2026-01-28"
    }
  ]
}
```

**Frontend Usage**:
```javascript
const reviews = await fetch(`/api/property/${propertyId}/reviews?days=30`)
  .then(r => r.json());

// Display stats
document.querySelector('.total-reviews').textContent = reviews.total_reviews;
document.querySelector('.avg-rating').textContent = reviews.avg_rating.toFixed(1);

// Rating distribution bar chart
Object.entries(reviews.rating_distribution).forEach(([rating, count]) => {
  const percentage = (count / reviews.total_reviews) * 100;
  createRatingBar(rating, percentage);
});
```

---

#### GET `/api/property/{property_id}/amenities`
Get property amenities with competitor gaps

**Response**:
```json
{
  "property_id": "PROP_001",
  "amenities": [
    {
      "name": "Free WiFi",
      "available": true,
      "competitor_coverage": null
    },
    {
      "name": "Gym",
      "available": false,
      "competitor_coverage": "4/5 competitors have this"
    }
  ],
  "missing_critical": ["Gym", "Free Breakfast"],
  "gap_count": 3
}
```

**Frontend Usage**:
```javascript
const amenities = await fetch(`/api/property/${propertyId}/amenities`)
  .then(r => r.json());

amenities.amenities.forEach(amenity => {
  addAmenityItem({
    name: amenity.name,
    available: amenity.available,
    icon: amenity.available ? '✓' : '✗',
    gap: amenity.competitor_coverage
  });
});

// Show gap alert
if (amenities.missing_critical.length > 0) {
  showAlert(`Missing ${amenities.missing_critical.join(', ')}`);
}
```

---

#### GET `/api/property/{property_id}/booking-trends?days=30`
Get booking trends chart data

**Response**:
```json
{
  "property_id": "PROP_001",
  "period_start": "2026-01-01",
  "period_end": "2026-01-30",
  "trends": [
    {
      "date": "2026-01-01",
      "occupancy": 73.0,
      "bookings": 69,
      "avg_rate": 4248.0
    }
    // ... more data points
  ],
  "avg_occupancy": 70.6,
  "trend_direction": "declining"
}
```

**Frontend Usage**:
```javascript
const trends = await fetch(`/api/property/${propertyId}/booking-trends?days=30`)
  .then(r => r.json());

// Line chart
const chartData = trends.trends.map(t => ({
  date: t.date,
  occupancy: t.occupancy,
  bookings: t.bookings
}));

// Trend indicator
const trendIcon = trends.trend_direction === 'improving' ? '📈' : 
                  trends.trend_direction === 'declining' ? '📉' : '➡️';
```

---

#### GET `/api/property/{property_id}/weather-impact?days=30`
Get weather impact data

**Response**:
```json
{
  "property_id": "PROP_001",
  "city": "Lonavala",
  "period_start": "2026-01-01",
  "period_end": "2026-01-30",
  "weather_data": [
    {
      "date": "2026-01-01",
      "weather_type": "Rainy",
      "temperature": 28.5,
      "rainfall_mm": 75.0
    }
    // ... more data points
  ],
  "rainy_days": 16,
  "extreme_events": [
    {
      "type": "heavy_rainfall",
      "severity": "high",
      "days_affected": 16,
      "impact": "Likely deterred leisure and business travel"
    }
  ],
  "impact_assessment": "high"
}
```

**Frontend Usage**:
```javascript
const weather = await fetch(`/api/property/${propertyId}/weather-impact?days=30`)
  .then(r => r.json());

// Weather chart
const chartData = weather.weather_data.map(w => ({
  date: w.date,
  rainfall: w.rainfall_mm,
  temperature: w.temperature
}));

// Impact badge
const impactBadge = document.querySelector('.weather-impact');
impactBadge.textContent = weather.impact_assessment.toUpperCase();
impactBadge.className = `badge ${weather.impact_assessment}`;  // "high" | "medium" | "low"
```

---

### 3. Analysis APIs

#### POST `/api/analysis/start`
Start AI analysis for a property

**Request Body**:
```json
{
  "property_id": "PROP_001",
  "analysis_date": "2026-01-29",  // optional, defaults to today
  "lookback_days": 30  // optional, default: 30, range: 7-90
}
```

**Response**:
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "started",
  "message": "Analysis started successfully"
}
```

**Frontend Usage**:
```javascript
// On "Analyze" button click
const startAnalysis = async (propertyId) => {
  const response = await fetch('/api/analysis/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      property_id: propertyId,
      lookback_days: 30
    })
  });
  
  const data = await response.json();
  
  // Store analysis_id and start polling
  const analysisId = data.analysis_id;
  pollAnalysisStatus(analysisId);
};
```

---

#### GET `/api/analysis/{analysis_id}/status`
Check analysis status (for polling)

**Response**:
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "property_id": "PROP_001",
  "status": "processing",  // "queued" | "processing" | "completed" | "failed"
  "progress": 45,  // 0-100
  "started_at": "2026-01-31T16:57:21.001Z",
  "completed_at": null,
  "error_message": null
}
```

**Frontend Usage**:
```javascript
// Poll status every 2 seconds
const pollAnalysisStatus = async (analysisId) => {
  const interval = setInterval(async () => {
    const status = await fetch(`/api/analysis/${analysisId}/status`)
      .then(r => r.json());
    
    // Update progress bar
    updateProgressBar(status.progress);
    
    if (status.status === 'completed') {
      clearInterval(interval);
      // Redirect to results page
      window.location.href = `/analysis/${analysisId}`;
    } else if (status.status === 'failed') {
      clearInterval(interval);
      showError(status.error_message);
    }
  }, 2000);
};
```

---

#### GET `/api/analysis/{analysis_id}/result`
Get complete analysis result

**Response** (Large - showing structure):
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "property_id": "PROP_001",
  "property_name": "Grand Harriot Downtown",
  "analysis_date": "2026-01-29",
  "current_occupancy": 70.6,
  
  "rca": {
    "property_id": "PROP_001",
    "analysis_date": "2026-01-29",
    "overall_confidence": 0.82,
    "primary_causes": [
      {
        "cause": "Poor Guest Experience (Wi-Fi + Cleanliness)",
        "confidence": 1.0,
        "impact_level": "high",
        "supporting_signals": {
          "wifi_complaints": 8,
          "cleanliness_mentions": 6,
          "negative_reviews": "100%"
        }
      },
      {
        "cause": "Price-Value Disconnect (49% premium)",
        "confidence": 0.90,
        "impact_level": "high",
        "supporting_signals": {
          "price_gap": "49.22%",
          "positioning": "premium"
        }
      }
    ],
    "explanation": "Occupancy dropped due to premium pricing without matching quality..."
  },
  
  "actions": {
    "property_id": "PROP_001",
    "target_segment": "26-35",
    "recommended_actions": [
      {
        "action_id": "action_1",
        "action_type": "operations",
        "priority": 1,
        "campaign_name": null,
        "description": "Upgrade Wi-Fi to 500 Mbps fiber...",
        "reason": "Addresses #1 complaint",
        "timeline": "1 week",
        "budget_estimate": "medium",
        "predicted_uplift": "10-15%",
        "confidence": 0.85
      }
      // ... more actions
    ],
    "total_actions": 8,
    "priority_1_count": 2,
    "rationale": "Strategy prioritizes high-impact causes..."
  },
  
  "impact": {
    "property_id": "PROP_001",
    "current_occupancy": 70.6,
    "projected_occupancy": 94.9,
    "individual_predictions": [
      {
        "action_description": "Wi-Fi upgrade",
        "predicted_increase": "10-15%",
        "confidence_level": "85%",
        "time_to_impact": "1-2 weeks",
        "rationale": "Wi-Fi critical for target segment...",
        "risk_factors": ["Execution quality", "Communication needed"]
      }
    ],
    "combined_impact": {
      "min_increase": "18.5%",
      "max_increase": "31.7%",
      "most_likely_increase": "24.3%",
      "methodology": "Compounding formula"
    },
    "summary": "Expected 24.3% occupancy increase...",
    "high_confidence_actions": 5
  },
  
  "status": "completed",
  "generated_at": "2026-01-31T16:58:16.308Z"
}
```

**Frontend Usage - RCA Section**:
```javascript
const result = await fetch(`/api/analysis/${analysisId}/result`)
  .then(r => r.json());

// Display RCA
result.rca.primary_causes.forEach(cause => {
  createRCACard({
    title: cause.cause,
    confidence: `${(cause.confidence * 100).toFixed(0)}%`,
    impact: cause.impact_level,  // "high" | "medium" | "low"
    signals: cause.supporting_signals
  });
});

// Explanation
document.querySelector('.rca-explanation').textContent = result.rca.explanation;
```

**Frontend Usage - Action Cards**:
```javascript
// Display action cards (like your design)
result.actions.recommended_actions.forEach(action => {
  createActionCard({
    type: action.action_type.toUpperCase(),  // "PRICING", "INVENTORY", etc.
    confidence: action.confidence ? `${(action.confidence * 100).toFixed(0)}% Conf.` : null,
    title: action.description.substring(0, 50),
    description: action.reason,
    uplift: action.predicted_uplift,  // "+$1,450 /day"
    priority: action.priority,
    budget: action.budget_estimate
  });
});
```

**Frontend Usage - Impact Forecast**:
```javascript
// Display impact metrics
const impact = result.impact;

document.querySelector('.current-occupancy').textContent = `${impact.current_occupancy}%`;
document.querySelector('.projected-occupancy').textContent = `${impact.projected_occupancy.toFixed(1)}%`;
document.querySelector('.expected-increase').textContent = impact.combined_impact.most_likely_increase;

// Impact range
document.querySelector('.min-increase').textContent = impact.combined_impact.min_increase;
document.querySelector('.max-increase').textContent = impact.combined_impact.max_increase;
```

---

## 🔄 Complete Frontend Workflow

### Dashboard Page
```javascript
// Load dashboard on mount
useEffect(() => {
  Promise.all([
    fetch('/api/dashboard/metrics').then(r => r.json()),
    fetch('/api/dashboard/portfolio').then(r => r.json())
  ]).then(([metrics, portfolio]) => {
    setMetrics(metrics);
    setProperties(portfolio.properties);
  });
}, []);

// Handle property click
const handlePropertyClick = (propertyId) => {
  navigate(`/property/${propertyId}`);
};
```

### Property Detail Page
```javascript
// Load all property data
useEffect(() => {
  const propertyId = params.propertyId;
  const days = 30;
  
  Promise.all([
    fetch(`/api/property/${propertyId}/competitor-pricing?days=${days}`),
    fetch(`/api/property/${propertyId}/reviews?days=${days}`),
    fetch(`/api/property/${propertyId}/amenities`),
    fetch(`/api/property/${propertyId}/booking-trends?days=${days}`),
    fetch(`/api/property/${propertyId}/weather-impact?days=${days}`)
  ]).then(responses => 
    Promise.all(responses.map(r => r.json()))
  ).then(([pricing, reviews, amenities, trends, weather]) => {
    setCompetitorPricing(pricing);
    setReviews(reviews);
    setAmenities(amenities);
    setBookingTrends(trends);
    setWeatherData(weather);
  });
}, [params.propertyId]);

// Handle analyze button
const handleAnalyze = async () => {
  const response = await fetch('/api/analysis/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      property_id: propertyId,
      lookback_days: 30
    })
  });
  
  const { analysis_id } = await response.json();
  setAnalysisId(analysis_id);
  setShowProgressModal(true);
  pollAnalysisStatus(analysis_id);
};
```

### Analysis Results Page
```javascript
// Load analysis result
useEffect(() => {
  const analysisId = params.analysisId;
  
  fetch(`/api/analysis/${analysisId}/result`)
    .then(r => r.json())
    .then(result => {
      setAnalysisResult(result);
      setLoading(false);
    });
}, [params.analysisId]);

// Render sections
return (
  <>
    <RCASection causes={analysisResult.rca.primary_causes} />
    <ActionCardsGrid actions={analysisResult.actions.recommended_actions} />
    <ImpactForecast impact={analysisResult.impact} />
  </>
);
```

---

## 🔐 Error Handling

All endpoints return errors in this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "status_code": 404
}
```

**Frontend Error Handling**:
```javascript
const apiCall = async (url, options) => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.error);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showToast(error.message, 'error');
    throw error;
  }
};
```

---

## 🧪 Testing the API

### Using cURL

```bash
# Dashboard metrics
curl http://localhost:3000/api/dashboard/metrics

# Start analysis
curl -X POST http://localhost:3000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{"property_id":"PROP_001","lookback_days":30}'

# Get result
curl http://localhost:3000/api/analysis/{analysis_id}/result
```

### Using Swagger UI

Visit `http://localhost:3000/docs` for interactive API testing.

---

## 📊 Data Flow Summary

```
Dashboard Page:
GET /api/dashboard/metrics → Display metrics cards
GET /api/dashboard/portfolio → Display property table

↓ User clicks property

Property Detail Page:
GET /api/property/{id}/competitor-pricing → Chart
GET /api/property/{id}/reviews → Stats + recent reviews
GET /api/property/{id}/amenities → Amenities list
GET /api/property/{id}/booking-trends → Trends chart
GET /api/property/{id}/weather-impact → Weather chart

↓ User clicks "Analyze" button

POST /api/analysis/start → Get analysis_id
Poll GET /api/analysis/{id}/status → Show progress

↓ Analysis complete (status = "completed")

Redirect to Analysis Results Page:
GET /api/analysis/{id}/result → Display RCA + Actions + Impact
```

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Change CORS origins to specific frontend URL
- [ ] Add authentication/authorization
- [ ] Move analysis jobs to Redis/database
- [ ] Add rate limiting
- [ ] Set up proper logging and monitoring
- [ ] Add API versioning
- [ ] Implement caching for dashboard data
- [ ] Add request validation middleware
- [ ] Set up HTTPS
- [ ] Configure environment-specific settings

---

**API is ready for frontend integration!** 🎉

All endpoints tested and documented. Your dashboard design maps perfectly to these APIs.
