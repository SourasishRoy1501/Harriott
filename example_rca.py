"""
Simple example of using RCA Agent

This shows the easiest way to analyze a property.
"""

from datetime import date
from src.agents.rca_agent import analyze_property_rca

# Analyze a property
result = analyze_property_rca(
    property_id="97e0f2d2-fc8e-48d4-91c5-9c77cbc4b12c",  # Replace with your property ID
    analysis_date=date(2026, 1, 29),  # Or use date.today()
    lookback_days=30
)

# Print results
print("=" * 80)
print("ROOT CAUSE ANALYSIS")
print("=" * 80)
print(f"\nProperty: {result.property_id}")
print(f"Confidence: {result.overall_confidence:.0%}")

print(f"\n🔍 ROOT CAUSES:")
for i, cause in enumerate(result.primary_causes, 1):
    print(f"\n{i}. {cause.cause}")
    print(f"   Impact: {cause.impact_level} | Confidence: {cause.confidence:.0%}")

print(f"\n📋 SUMMARY:")
print(result.natural_language_explanation)
print("\n" + "=" * 80)
