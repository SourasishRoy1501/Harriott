"""
Date and time utilities for SOA
"""
from datetime import date, datetime, timedelta
from typing import Tuple, List


def get_date_range(end_date: date, lookback_days: int) -> Tuple[date, date]:
    """
    Calculate start and end date for analysis period
    
    Args:
        end_date: End date of analysis
        lookback_days: Number of days to look back
        
    Returns:
        Tuple of (start_date, end_date)
    """
    start_date = end_date - timedelta(days=lookback_days)
    return start_date, end_date


def split_date_range(start_date: date, end_date: date) -> Tuple[Tuple[date, date], Tuple[date, date]]:
    """
    Split date range into two equal periods for comparison
    
    Args:
        start_date: Start of range
        end_date: End of range
        
    Returns:
        Tuple of ((period1_start, period1_end), (period2_start, period2_end))
    """
    total_days = (end_date - start_date).days
    mid_point = start_date + timedelta(days=total_days // 2)
    
    period1 = (start_date, mid_point)
    period2 = (mid_point + timedelta(days=1), end_date)
    
    return period1, period2


def get_week_dates(reference_date: date) -> List[date]:
    """
    Get all dates in the same week as reference date
    
    Args:
        reference_date: Reference date
        
    Returns:
        List of dates in the week (Monday to Sunday)
    """
    # Find Monday of the week
    monday = reference_date - timedelta(days=reference_date.weekday())
    
    return [monday + timedelta(days=i) for i in range(7)]


def is_weekend(check_date: date) -> bool:
    """
    Check if date is a weekend
    
    Args:
        check_date: Date to check
        
    Returns:
        True if Saturday or Sunday
    """
    return check_date.weekday() >= 5


def get_season(check_date: date) -> str:
    """
    Determine season for a given date (Northern Hemisphere)
    
    Args:
        check_date: Date to check
        
    Returns:
        Season name: spring, summer, fall, winter
    """
    month = check_date.month
    
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def format_date_range(start_date: date, end_date: date) -> str:
    """
    Format date range as human-readable string
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Formatted string like "Jan 1, 2024 - Jan 31, 2024"
    """
    return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"


def days_between(date1: date, date2: date) -> int:
    """
    Calculate number of days between two dates
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        Number of days (absolute value)
    """
    return abs((date2 - date1).days)


def get_today() -> date:
    """
    Get today's date
    
    Returns:
        Today's date
    """
    return datetime.now().date()


def parse_date_string(date_str: str) -> date:
    """
    Parse date string in ISO format (YYYY-MM-DD)
    
    Args:
        date_str: Date string
        
    Returns:
        Date object
        
    Raises:
        ValueError: If date string is invalid
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()
