"""
Date parsing utilities for basketball season (Nov-Mar spanning two calendar years)
"""
from datetime import datetime


def parse_game_date(date_str):
    """
    Convert 'Nov 14' format to sortable datetime for basketball season
    Handles season spanning two calendar years (Nov-Dec 2024, Jan-Mar 2025)

    Args:
        date_str: Date string in 'Mon DD' format (e.g., 'Nov 14', 'Jan 20')

    Returns:
        datetime object with proper year
    """
    try:
        date_obj = datetime.strptime(date_str, '%b %d')
        month = date_obj.month

        # Nov-Dec are in 2024, Jan-Mar are in 2025
        year = 2024 if month >= 11 else 2025

        return datetime(year, month, date_obj.day)
    except (ValueError, AttributeError):
        # Return far future date for invalid dates (sorts to end)
        return datetime(2099, 12, 31)
