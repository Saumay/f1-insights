"""Telemetry analysis utilities for F1 data."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from fastf1.core import CircuitInfo
import fastf1

def get_straight_section_telemetry(
    telemetry: pd.DataFrame,
    start_corner: str,
    end_corner: str,
    circuit: CircuitInfo
) -> pd.DataFrame:
    """Extract telemetry data for a specific section of the circuit.
    
    Args:
        telemetry: DataFrame containing telemetry data
        start_corner: Name of the starting corner
        end_corner: Name of the ending corner
        circuit: CircuitInfo object containing circuit data
        
    Returns:
        DataFrame containing telemetry data for the specified section
    """
    # Get corner distances
    corners = circuit.corners
    start_corner_data = corners[corners['Number'] == start_corner]
    end_corner_data = corners[corners['Number'] == end_corner]
    
    if start_corner_data.empty or end_corner_data.empty:
        print(f"Warning: Could not find corners {start_corner} or {end_corner}")
        return pd.DataFrame()  # Return empty DataFrame if corners not found
    
    start_distance = start_corner_data['Distance'].iloc[0]
    end_distance = end_corner_data['Distance'].iloc[0]
    
    # Extract section between corners
    section = telemetry[
        (telemetry['Distance'] >= start_distance) &
        (telemetry['Distance'] <= end_distance)
    ]
    
    return section

def analyze_slipstream(
    telemetry: pd.DataFrame,
    min_distance: float = 50.0,
    min_speed: float = 300.0
) -> Tuple[bool, float, float]:
    """Analyze telemetry data for slipstream effects.
    
    Args:
        telemetry: DataFrame containing telemetry data
        min_distance: Minimum distance to consider for slipstream (meters)
        min_speed: Minimum speed to consider for slipstream (km/h)
        
    Returns:
        Tuple containing:
        - Boolean indicating if slipstream was detected
        - Minimum distance to car ahead
        - Maximum speed in the section
    """
    # Get minimum distance to car ahead
    min_dist = telemetry['DistanceToCarAhead'].min()
    
    # Get maximum speed
    max_speed = telemetry['Speed'].max()
    
    # Check for slipstream conditions
    has_slipstream = (min_dist < min_distance) and (max_speed > min_speed)
    
    return has_slipstream, min_dist, max_speed

def get_driver_lap_telemetry(
    session: fastf1.core.Session,
    driver: str,
    lap_number: Optional[int] = None
) -> pd.DataFrame:
    """Get telemetry data for a specific driver's lap.
    
    Args:
        session: FastF1 session object
        driver: Driver code (e.g., 'VER')
        lap_number: Optional lap number. If None, uses fastest lap.
        
    Returns:
        DataFrame containing telemetry data
    """
    # Get driver's laps
    driver_laps = session.laps[session.laps['Driver'] == driver]
    
    if driver_laps.empty:
        print(f"No laps found for driver {driver}")
        return pd.DataFrame()
    
    # Get the specified lap or fastest lap
    if lap_number is not None:
        lap = driver_laps[driver_laps['LapNumber'] == lap_number]
    else:
        lap = driver_laps.pick_fastest()
    
    if lap.empty:
        print(f"No lap found for driver {driver}")
        return pd.DataFrame()
    
    # Get telemetry data
    return lap.get_telemetry() 