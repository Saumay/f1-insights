#!/usr/bin/env python3
"""Script to analyze slipstream effects in F1 races."""

import os
import fastf1
from f1_insights.utils.telemetry_utils import (
    get_driver_lap_telemetry,
    get_straight_section_telemetry,
    analyze_slipstream
)

def print_available_corners(session: fastf1.core.Session) -> None:
    """Print available corner names for the circuit.
    
    Args:
        session: FastF1 session object
    """
    circuit = session.get_circuit_info()
    print("\nAvailable corners:")
    for _, row in circuit.corners.iterrows():
        print(f"- {row['Number']} (Distance: {row['Distance']:.0f}m)")

def analyze_slipstream_for_driver(
    session: fastf1.core.Session,
    driver: str,
    start_corner: str,
    end_corner: str
) -> None:
    """Analyze slipstream effects for a specific driver.
    
    Args:
        session: FastF1 session object
        driver: Driver code (e.g., 'VER')
        start_corner: Name of the starting corner
        end_corner: Name of the ending corner
    """
    # Get driver's fastest lap telemetry
    telemetry = get_driver_lap_telemetry(session, driver)
    
    if telemetry.empty:
        print(f"No telemetry data found for {driver}")
        return
    
    # Get section telemetry
    section = get_straight_section_telemetry(
        telemetry,
        start_corner,
        end_corner,
        session.get_circuit_info()
    )
    
    if section.empty:
        print(f"No telemetry data found for {driver} between {start_corner} and {end_corner}")
        return
    
    # Analyze slipstream
    has_slipstream, min_dist, max_speed = analyze_slipstream(section)
    
    # Print results
    print(f"\nDriver: {driver}")
    print(f"Section: {start_corner} to {end_corner}")
    print(f"Minimum distance to car ahead: {min_dist:.1f}m")
    print(f"Maximum speed: {max_speed:.1f} km/h")
    print(f"Slipstream detected: {'Yes' if has_slipstream else 'No'}")

def main():
    """Main function to analyze slipstream effects."""
    try:
        # Enable caching
        cache_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'cache'))
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)
        
        # Load session data
        session = fastf1.get_session(2024, 'Chinese GP', 'SQ')
        session.load()
        
        # Print available corners
        print_available_corners(session)
        
        # Define drivers to analyze
        drivers = ['VER', 'HAM', 'PER', 'LEC', 'SAI', 'NOR']
        
        # Define sections to analyze (using correct corner names)
        sections = [
            ('Turn 1', 'Turn 2'),  # First complex
            ('Turn 6', 'Turn 7'),  # Back straight
            ('Turn 13', 'Turn 14')  # Final complex
        ]
        
        # Analyze each driver
        for driver in drivers:
            print(f"\nAnalyzing {driver}...")
            for start_corner, end_corner in sections:
                analyze_slipstream_for_driver(session, driver, start_corner, end_corner)
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    main() 