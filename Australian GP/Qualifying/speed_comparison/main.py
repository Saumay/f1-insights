"""Overlaying speed traces of all drivers' fastest laps
================================================
Compare all drivers' fastest qualifying laps by overlaying their speed traces.
"""
import matplotlib.pyplot as plt
import fastf1.plotting
import pandas as pd
import numpy as np

# Enable Matplotlib patches for plotting timedelta values and load
# FastF1's dark color scheme
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                          color_scheme='fastf1')

# Load a session and its telemetry data
session = fastf1.get_session(2025, 'Australia', 'Q')
session.load()

# Get the list of all drivers who participated in the session
all_drivers = session.results['Abbreviation'].tolist()
print(f"Found {len(all_drivers)} drivers in the session")

# Create figure and axis objects
fig, ax = plt.subplots(figsize=(14, 8))

# Function to smooth the speed data to reduce noise and make the plot clearer
def smooth_data(data, window_size=5):
    return pd.Series(data).rolling(window=window_size, center=True).mean().fillna(method='bfill').fillna(method='ffill').values

# Plot speed traces for each driver with a slight transparency
for driver in all_drivers:
    try:
        # Get the fastest lap for the current driver
        driver_lap = session.laps.pick_drivers(driver).pick_fastest()
        
        if driver_lap.empty:
            print(f"No valid lap found for {driver}")
            continue
            
        # Get telemetry data and add distance
        driver_tel = driver_lap.get_car_data().add_distance()
        
        if driver_tel.empty:
            print(f"No telemetry data for {driver}")
            continue
            
        # Get the team color
        try:
            team_color = fastf1.plotting.get_team_color(driver_lap['Team'], session=session)
        except:
            # Fallback if team color is not available
            team_color = 'gray'
        
        # Smooth the speed data
        smoothed_speed = smooth_data(driver_tel['Speed'])
        
        # Plot the speed trace
        ax.plot(driver_tel['Distance'], smoothed_speed, color=team_color, label=driver, alpha=0.8, linewidth=1.5)
        
        print(f"Plotted data for {driver}")
    except Exception as e:
        print(f"Error plotting data for {driver}: {e}")

# Set axis labels
ax.set_xlabel('Distance (m)', fontsize=12)
ax.set_ylabel('Speed (km/h)', fontsize=12)

# Add grid for better readability
ax.grid(True, alpha=0.3, linestyle='--')

# Add legend outside the plot for better visibility
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

# Add track sectors as vertical lines
try:
    lap_info = session.laps.pick_fastest()
    sector1 = lap_info['Sector1SessionTime'] - lap_info['LapStartTime']
    sector2 = lap_info['Sector2SessionTime'] - lap_info['LapStartTime']
    
    # Map these time deltas to distance
    fastest_lap_tel = lap_info.get_car_data().add_distance()
    s1_distance = fastest_lap_tel['Distance'].iloc[np.argmin(np.abs(fastest_lap_tel['Time'] - sector1))]
    s2_distance = fastest_lap_tel['Distance'].iloc[np.argmin(np.abs(fastest_lap_tel['Time'] - sector2))]
    
    # Plot sector lines
    ax.axvline(x=s1_distance, color='white', linestyle='--', alpha=0.8, label='Sector 1/2')
    ax.axvline(x=s2_distance, color='white', linestyle='--', alpha=0.8, label='Sector 2/3')
    
    # Add sector annotations
    y_pos = ax.get_ylim()[1] * 0.95
    ax.text(s1_distance/2, y_pos, "Sector 1", ha='center', va='top', color='white', bbox=dict(facecolor='black', alpha=0.5))
    ax.text(s1_distance + (s2_distance-s1_distance)/2, y_pos, "Sector 2", ha='center', va='top', color='white', bbox=dict(facecolor='black', alpha=0.5))
    ax.text(s2_distance + (fastest_lap_tel['Distance'].max()-s2_distance)/2, y_pos, "Sector 3", ha='center', va='top', color='white', bbox=dict(facecolor='black', alpha=0.5))
except Exception as e:
    print(f"Could not add sector lines: {e}")

# Add title
plt.suptitle(f"All Drivers' Fastest Lap Speed Comparison\n"
             f"{session.event['EventName']} {session.event.year} Qualifying", 
             fontsize=16)

# Ensure tight layout
plt.tight_layout(rect=[0, 0, 0.85, 0.95])

# Save the figure
plt.savefig(f'Australian_GP_2025_All_Drivers_Speed_Comparison.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

# Create a second visualization - Minimum/Maximum speed by track position
try:
    print("Creating min/max speed envelope plot...")
    
    # Create a new figure
    fig2, ax2 = plt.subplots(figsize=(14, 8))
    
    # Initialize lists to store all speed values at each distance point
    all_speeds = {}
    
    # Distance sampling resolution (in meters)
    resolution = 10
    
    # Collect speed data from all drivers
    for driver in all_drivers:
        try:
            # Get the fastest lap for the current driver
            driver_lap = session.laps.pick_drivers(driver).pick_fastest()
            
            if driver_lap.empty:
                continue
                
            # Get telemetry data and add distance
            driver_tel = driver_lap.get_car_data().add_distance()
            
            if driver_tel.empty:
                continue
                
            # Sample speeds at regular distance intervals
            for d in range(0, int(driver_tel['Distance'].max()), resolution):
                # Find the closest point in the data
                idx = np.argmin(np.abs(driver_tel['Distance'] - d))
                distance = int(driver_tel['Distance'].iloc[idx] / resolution) * resolution
                
                if distance not in all_speeds:
                    all_speeds[distance] = []
                
                all_speeds[distance].append(driver_tel['Speed'].iloc[idx])
                
        except Exception as e:
            print(f"Error processing data for {driver} in min/max plot: {e}")
    
    # Convert to arrays for plotting
    distances = sorted(all_speeds.keys())
    min_speeds = [min(all_speeds[d]) if all_speeds[d] else 0 for d in distances]
    max_speeds = [max(all_speeds[d]) if all_speeds[d] else 0 for d in distances]
    median_speeds = [np.median(all_speeds[d]) if all_speeds[d] else 0 for d in distances]
    
    # Smooth the arrays
    min_speeds = smooth_data(min_speeds, window_size=5)
    max_speeds = smooth_data(max_speeds, window_size=5)
    median_speeds = smooth_data(median_speeds, window_size=5)
    
    # Plot the envelope
    ax2.fill_between(distances, min_speeds, max_speeds, alpha=0.3, color='lightblue', label='Speed Range')
    ax2.plot(distances, median_speeds, color='blue', linewidth=2, label='Median Speed')
    
    # Set axis labels
    ax2.set_xlabel('Distance (m)', fontsize=12)
    ax2.set_ylabel('Speed (km/h)', fontsize=12)
    
    # Add grid
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Try to add corner numbers
    try:
        circuit_info = session.get_circuit_info()
        if circuit_info is not None and 'Corners' in circuit_info:
            corners = circuit_info['Corners']
            
            # Create a mapping from distance to corner number
            corner_mapping = {}
            
            # This is a simplification - ideally we'd have exact corner distances
            # but we'll approximate based on the speed profile
            # Find local minima in the median speed profile which likely indicate corners
            speed_diffs = np.diff(median_speeds)
            potential_corners = []
            
            for i in range(1, len(speed_diffs) - 1):
                if speed_diffs[i-1] < 0 and speed_diffs[i] > 0:
                    # Local minimum
                    potential_corners.append((distances[i], median_speeds[i]))
            
            # If we have as many potential corners as actual corners, map them
            if len(potential_corners) >= len(corners):
                for i, corner in enumerate(corners):
                    if i < len(potential_corners):
                        corner_dist = potential_corners[i][0]
                        corner_speed = potential_corners[i][1]
                        ax2.text(corner_dist, corner_speed - 20, str(corner['Number']), 
                               fontsize=9, ha='center', va='top', 
                               bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
    except Exception as e:
        print(f"Could not add corner annotations: {e}")
    
    # Add title and legend
    ax2.legend(loc='upper right')
    plt.suptitle(f"Speed Range Across All Drivers\n"
                 f"{session.event['EventName']} {session.event.year} Qualifying", 
                 fontsize=16)
    
    # Ensure tight layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Save the figure
    plt.savefig(f'Australian_GP_2025_Speed_Range.png', dpi=300, bbox_inches='tight')
    
    # Show the plot
    plt.show()
    
except Exception as e:
    print(f"Error creating min/max speed envelope plot: {e}")
    