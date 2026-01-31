"""
Supabase client connection and utilities
"""
from supabase import create_client, Client
from typing import Optional
from loguru import logger
from config.settings import get_settings


_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance (singleton pattern)
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        
        try:
            _supabase_client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    return _supabase_client


def test_connection() -> bool:
    """
    Test Supabase connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_supabase_client()
        # Try to query properties table
        response = client.table("properties").select("id").limit(1).execute()
        logger.info("Supabase connection test successful")
        return True
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False
