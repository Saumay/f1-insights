import fastf1
import pandas as pd

"""Utilities for handling F1 driver information."""

def get_driver_info(session, driver_code):
    """Get driver's full information from their three-letter code.
    
    Args:
        session: FastF1 session object
        driver_code: Three-letter driver code (e.g., 'HAM', 'VER')
        
    Returns:
        dict: Driver information containing name, number, and team.
              Returns default values if driver not found.
              
    Example:
        >>> session = fastf1.get_session(2025, 'China', 'SQ')
        >>> session.load()
        >>> info = get_driver_info(session, 'HAM')
        >>> print(info)
        {'name': 'Lewis Hamilton', 'number': '44', 'team': 'Ferrari'}
    """
    default_info = {
        'name': driver_code,
        'number': 'N/A',
        'team': 'Unknown'
    }
    
    driver_data = session.results.loc[session.results['Abbreviation'] == driver_code]
    if driver_data.empty:
        return default_info
    
    return {
        'name': f"{driver_data['FirstName'].iloc[0]} {driver_data['LastName'].iloc[0]}",
        'number': driver_data['DriverNumber'].iloc[0],
        'team': driver_data['TeamName'].iloc[0]
    }

