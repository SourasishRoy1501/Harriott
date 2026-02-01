"""
Complete End-to-End Example

This demonstrates the full SOA workflow:
1. RCA Agent → Diagnoses root causes
2. Action Strategy Agent → Generates campaigns
3. Impact Predictor Agent → Predicts occupancy impact
"""

from datetime import date
from src.agents.rca_agent import analyze_property_rca
from src.agents.action_strategy_agent import generate_action_strategy
from src.agents.impact_predictor_agent import predict_action_impact
from src.models.schemas import AgeSegment

# Configuration
PROPERTY_ID = "87085c36-4993-40d8-a3e8-3ef8985b235c"  # Replace with your property
ANALYSIS_DATE = date(2026, 1, 29)
LOOKBACK_DAYS = 30
TARGET_SEGMENT = AgeSegment.YOUNG_PROFESSIONAL  # 26-35 age group
CURRENT_OCCUPANCY = 70.6  # Current average occupancy %

print("=" * 80)
print("HARRIOT SMART OCCUPANCY AGENT - COMPLETE ANALYSIS")
print("=" * 80)

# ============================================================================
# STEP 1: ROOT CAUSE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: ROOT CAUSE ANALYSIS")
print("=" * 80)
print("\nAnalyzing property performance...")

rca_result = analyze_property_rca(
    property_id=PROPERTY_ID,
    analysis_date=ANALYSIS_DATE,
    lookback_days=LOOKBACK_DAYS
)

print(f"\nProperty: {rca_result.property_id}")
print(f"Overall Confidence: {rca_result.overall_confidence:.0%}")

print(f"\n🔍 ROOT CAUSES ({len(rca_result.primary_causes)}):")
print("-" * 80)
for i, cause in enumerate(rca_result.primary_causes, 1):
    print(f"\n{i}. {cause.cause}")
    print(f"   Impact: {cause.impact_level.upper()} | Confidence: {cause.confidence:.0%}")
    print(f"   Signals: {cause.supporting_signals}")

print(f"\n📋 EXPLANATION:")
print("-" * 80)
print(rca_result.natural_language_explanation)

# ============================================================================
# STEP 2: ACTION STRATEGY
# ============================================================================
print("\n\n" + "=" * 80)
print("STEP 2: ACTION STRATEGY & CAMPAIGNS")
print("=" * 80)
print(f"\nTarget Segment: {TARGET_SEGMENT.value}")
print("Generating targeted campaigns...")

action_strategy = generate_action_strategy(
    rca_output=rca_result,
    target_segment=TARGET_SEGMENT,
    property_id=PROPERTY_ID
)

print(f"\n🎯 RECOMMENDED ACTIONS ({len(action_strategy.recommended_actions)}):")
print("-" * 80)

for i, action in enumerate(action_strategy.recommended_actions, 1):
    print(f"\n[Priority {action.priority}] {action.action_type.value.upper()}")
    print(f"Description: {action.description}")
    print(f"Reason: {action.reason}")
    print(f"Impact: {action.expected_impact}")
    print(f"Complexity: {action.implementation_complexity}")

print(f"\n📊 STRATEGY RATIONALE:")
print("-" * 80)
print(action_strategy.rationale)

# ============================================================================
# STEP 3: IMPACT PREDICTION
# ============================================================================
print("\n\n" + "=" * 80)
print("STEP 3: IMPACT PREDICTION")
print("=" * 80)
print(f"\nCurrent Occupancy: {CURRENT_OCCUPANCY}%")
print("Predicting occupancy impact...")

impact_predictions = predict_action_impact(
    rca_output=rca_result,
    action_strategy=action_strategy,
    current_occupancy=CURRENT_OCCUPANCY
)

print(f"\n📈 INDIVIDUAL ACTION IMPACTS:")
print("-" * 80)

for i, pred in enumerate(impact_predictions["individual_predictions"], 1):
    print(f"\n{i}. {pred.get('action_description', 'Action')[:80]}...")
    print(f"   Predicted Increase: {pred.get('predicted_occupancy_increase', 'N/A')}")
    print(f"   Confidence: {pred.get('confidence_level', 'N/A')}")
    print(f"   Time to Impact: {pred.get('time_to_impact', 'N/A')}")
    print(f"   Rationale: {pred.get('rationale', 'N/A')[:150]}...")
    
    if pred.get('risk_factors'):
        print(f"   Risks: {', '.join(pred['risk_factors'][:2])}")

print(f"\n🎯 COMBINED IMPACT FORECAST:")
print("-" * 80)
combined = impact_predictions["combined_impact"]
print(f"Best Case: {combined['max_increase']} occupancy increase")
print(f"Most Likely: {combined['most_likely_increase']} occupancy increase")
print(f"Worst Case: {combined['min_increase']} occupancy increase")
print(f"\nMethodology: {combined['methodology']}")

print(f"\n📝 EXECUTIVE SUMMARY:")
print("-" * 80)
print(impact_predictions["summary"])

# ============================================================================
# FINAL RECOMMENDATION
# ============================================================================
print("\n\n" + "=" * 80)
print("FINAL RECOMMENDATION")
print("=" * 80)

priority_1_actions = [
    a for a in action_strategy.recommended_actions
    if a.priority == 1
]

print(f"\n⚡ IMMEDIATE ACTIONS (Priority 1): {len(priority_1_actions)}")
print("-" * 80)
for action in priority_1_actions:
    print(f"• {action.description[:100]}...")

print(f"\n💰 EXPECTED ROI:")
print("-" * 80)
most_likely_increase = float(combined['most_likely_increase'].strip('%'))
current_occ = CURRENT_OCCUPANCY
new_occ = current_occ + (current_occ * most_likely_increase / 100)
print(f"Current Occupancy: {current_occ:.1f}%")
print(f"Projected Occupancy: {new_occ:.1f}%")
print(f"Absolute Increase: +{new_occ - current_occ:.1f} percentage points")

print(f"\n✅ NEXT STEPS:")
print("-" * 80)
print("1. Review and approve Priority 1 actions")
print("2. Allocate budget for immediate fixes")
print("3. Implement actions in priority order")
print("4. Monitor occupancy weekly")
print("5. Re-run analysis in 4 weeks to measure impact")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80 + "\n")