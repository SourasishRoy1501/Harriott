"""
Test script for RCA Agent

This script demonstrates how to use the RCA Agent to analyze property performance.
"""

from datetime import date, timedelta
from loguru import logger
import json

from src.agents.rca_agent import RCAAgent, analyze_property_rca
from src.database.queries import get_all_properties


def test_rca_agent_basic():
    """Test RCA agent with basic analysis"""
    logger.info("=" * 80)
    logger.info("TEST 1: Basic RCA Analysis")
    logger.info("=" * 80)
    
    # Get first property
    properties = get_all_properties()
    if not properties:
        logger.error("No properties found in database")
        return
    
    property_id = properties[0].id
    logger.info(f"Testing with property: {property_id} - {properties[0].name}")
    
    # Set analysis date
    analysis_date = date.today() - timedelta(days=1)  # Yesterday
    
    # Run analysis
    try:
        result = analyze_property_rca(
            property_id=property_id,
            analysis_date=analysis_date,
            lookback_days=30
        )
        
        logger.success("✓ RCA Analysis Complete!")
        print("\n" + "=" * 80)
        print("ROOT CAUSE ANALYSIS RESULTS")
        print("=" * 80)
        print(f"\nProperty: {property_id}")
        print(f"Analysis Date: {result.analysis_date}")
        print(f"Overall Confidence: {result.overall_confidence:.2f}")
        
        print(f"\n📊 PRIMARY ROOT CAUSES ({len(result.primary_causes)}):")
        print("-" * 80)
        for i, cause in enumerate(result.primary_causes, 1):
            print(f"\n{i}. {cause.cause}")
            print(f"   Confidence: {cause.confidence:.2f}")
            print(f"   Impact Level: {cause.impact_level.upper()}")
            print(f"   Supporting Signals:")
            for key, value in cause.supporting_signals.items():
                print(f"      - {key}: {value}")
        
        print(f"\n📝 EXPLANATION:")
        print("-" * 80)
        print(result.natural_language_explanation)
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"✗ RCA Analysis Failed: {e}")
        raise


def test_rca_agent_multiple_properties():
    """Test RCA agent with multiple properties"""
    logger.info("=" * 80)
    logger.info("TEST 2: Analyze Multiple Properties")
    logger.info("=" * 80)
    
    properties = get_all_properties()
    if len(properties) < 3:
        logger.warning("Need at least 3 properties for this test")
        return
    
    analysis_date = date.today() - timedelta(days=1)
    
    for i, prop in enumerate(properties[:3], 1):  # Test first 3 properties
        logger.info(f"\n[{i}/3] Analyzing: {prop.name} ({prop.id})")
        
        try:
            result = analyze_property_rca(
                property_id=prop.id,
                analysis_date=analysis_date,
                lookback_days=30
            )
            
            print(f"\n{prop.name} - Top Cause: {result.primary_causes[0].cause if result.primary_causes else 'N/A'}")
            print(f"Confidence: {result.overall_confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to analyze {prop.id}: {e}")


def test_rca_agent_detailed():
    """Test RCA agent with detailed output inspection"""
    logger.info("=" * 80)
    logger.info("TEST 3: Detailed Analysis Inspection")
    logger.info("=" * 80)
    
    # Initialize agent
    agent = RCAAgent()
    
    # Get property
    properties = get_all_properties()
    if not properties:
        logger.error("No properties found")
        return
    
    property_id = properties[0].id
    analysis_date = date.today() - timedelta(days=1)
    
    logger.info(f"Property: {property_id}")
    logger.info(f"Analysis Date: {analysis_date}")
    logger.info(f"Lookback: 30 days")
    
    # Run analysis
    result = agent.analyze(property_id, analysis_date, lookback_days=30)
    
    # Export to JSON
    result_dict = {
        "property_id": result.property_id,
        "analysis_date": str(result.analysis_date),
        "overall_confidence": result.overall_confidence,
        "primary_causes": [
            {
                "cause": cause.cause,
                "confidence": cause.confidence,
                "impact_level": cause.impact_level,
                "supporting_signals": cause.supporting_signals
            }
            for cause in result.primary_causes
        ],
        "explanation": result.natural_language_explanation
    }
    
    print("\n📄 JSON Output:")
    print("-" * 80)
    print(json.dumps(result_dict, indent=2))
    
    # Save to file
    output_file = f"rca_analysis_{property_id}_{analysis_date}.json"
    with open(output_file, 'w') as f:
        json.dump(result_dict, f, indent=2)
    
    logger.success(f"✓ Analysis saved to: {output_file}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("RCA AGENT TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        # Test 1: Basic analysis
        test_rca_agent_basic()
        
        print("\n\n")
        
        # Test 2: Multiple properties (optional - comment out if slow)
        # test_rca_agent_multiple_properties()
        
        print("\n\n")
        
        # Test 3: Detailed inspection
        # test_rca_agent_detailed()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logger.add(
        "logs/rca_agent_test.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    main()
