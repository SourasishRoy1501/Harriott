"""
Test script to verify Supabase connection and data access
"""
from loguru import logger
from datetime import date, timedelta

from config.settings import get_settings
from src.database.supabase_client import get_supabase_client, test_connection
from src.database.queries import (
    get_all_properties,
    get_property_by_id,
    get_booking_trends,
    get_reviews
)


def main():
    """Run basic tests"""
    logger.info("Starting SOA database connection test...")
    
    # Test 1: Settings
    logger.info("Test 1: Loading settings...")
    settings = get_settings()
    logger.success(f"✓ Settings loaded - Environment: {settings.environment}")
    
    # Test 2: Supabase connection
    logger.info("Test 2: Testing Supabase connection...")
    if test_connection():
        logger.success("✓ Supabase connection successful")
    else:
        logger.error("✗ Supabase connection failed")
        return
    
    # Test 3: Fetch properties
    logger.info("Test 3: Fetching properties...")
    properties = get_all_properties()
    if properties:
        logger.success(f"✓ Found {len(properties)} properties")
        for prop in properties[:3]:
            logger.info(f"  - {prop.name} ({prop.city})")
    else:
        logger.warning("No properties found")
        return
    
    # Test 4: Fetch booking trends for first property
    if properties:
        property_id = properties[0].id
        logger.info(f"Test 4: Fetching booking trends for {property_id}...")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        trends = get_booking_trends(property_id, start_date, end_date)
        if trends:
            logger.success(f"✓ Found {len(trends)} days of booking data")
            avg_occupancy = sum(t.occupancy_percentage for t in trends) / len(trends)
            logger.info(f"  Average occupancy: {avg_occupancy:.2f}%")
        else:
            logger.warning("No booking trends found")
    
    # Test 5: Fetch reviews
    if properties:
        logger.info(f"Test 5: Fetching reviews for {property_id}...")
        reviews = get_reviews(property_id, start_date, end_date)
        if reviews:
            logger.success(f"✓ Found {len(reviews)} reviews")
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            logger.info(f"  Average rating: {avg_rating:.2f}/5")
        else:
            logger.warning("No reviews found")
    
    logger.success("\n✓ All tests completed successfully!")


if __name__ == "__main__":
    main()
