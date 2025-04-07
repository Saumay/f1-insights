"""Compare multiple drivers' laps
=======================================================

Compare the last lap of Norris with the second last laps of Hamilton, Verstappen, Leclerc, and Piastri 
from the 2025 Chinese GP sprint qualifying session.
Shows the delta time relative to Hamilton's lap at each point on track.
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

# Enable Matplotlib patches for plotting timedelta values and load
# FastF1's dark color scheme
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                         color_scheme='fastf1')

# Load the session
session = fastf1.get_session(2025, 'China', 'SQ')
session.load()

# Get the specific laps
drivers = {
    'NOR': {'lap': session.laps.pick_driver('NOR').iloc[-1], 'label': 'Norris', 'team': 'MCL', 'color': '#8B4000'},  # Light orange for Norris
    'HAM': {'lap': session.laps.pick_driver('HAM').iloc[-2], 'label': 'Hamilton', 'team': 'FER'},
    'VER': {'lap': session.laps.pick_driver('VER').iloc[-2], 'label': 'Verstappen', 'team': 'RED'},
    'PIA': {'lap': session.laps.pick_driver('PIA').iloc[-2], 'label': 'Piastri', 'team': 'MCL'}
}

# Print lap numbers for verification
print(f"\nLap Numbers:")
for driver_code, driver_info in drivers.items():
    print(f"{driver_info['label']}: Lap {driver_info['lap']['LapNumber']}")

# Get telemetry data for all laps
telemetry_data = {}
for driver_code, driver_info in drivers.items():
    tel = driver_info['lap'].get_telemetry()
    tel['Time'] = tel['Time'] - tel['Time'].iloc[0]  # Normalize time to start from 0
    telemetry_data[driver_code] = tel

# Create the plot
fig, ax = plt.subplots(figsize=(15, 6))

# Interpolate the data to have the same number of points
max_distance = max(telemetry['Distance'].max() for telemetry in telemetry_data.values())
distance_points = np.linspace(0, max_distance, 1000)

# Get Hamilton's reference time progression
ham_interp = interp1d(telemetry_data['HAM']['Distance'], 
                     telemetry_data['HAM']['Time'],
                     bounds_error=False, fill_value='extrapolate')
ham_times = ham_interp(distance_points)

# Calculate and plot delta times for each driver
for driver_code, driver_info in drivers.items():
    if driver_code != 'HAM':
        # Create interpolation function for current driver
        driver_interp = interp1d(telemetry_data[driver_code]['Distance'],
                                telemetry_data[driver_code]['Time'],
                                bounds_error=False, fill_value='extrapolate')
        driver_times = driver_interp(distance_points)
        
        # Calculate delta times (positive means slower than Hamilton)
        delta_times = driver_times - ham_times
        
        # Plot delta times with custom color for Norris
        color = driver_info.get('color', fastf1.plotting.get_team_color(driver_info['team'], session=session))
        ax.plot(distance_points, delta_times,
                color=color,
                label=driver_info['label'], linewidth=2)

# Add zero reference line for Hamilton
ax.axhline(y=0, color=fastf1.plotting.get_team_color('FER', session=session),
           linestyle='-', label='Hamilton', linewidth=2)

# Add circuit corners
circuit_info = session.get_circuit_info()

# Draw vertical lines for corners
ax.vlines(x=circuit_info.corners['Distance'], 
          ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1],
          linestyles='dotted', colors='grey', alpha=0.5)

# Add corner numbers
for _, corner in circuit_info.corners.iterrows():
    txt = f"{corner['Number']}{corner['Letter']}"
    ax.text(corner['Distance'], ax.get_ylim()[0], txt,
            va='bottom', ha='center', size='small')

# Customize the plot
ax.set_xlabel('Distance in m')
ax.set_ylabel('Delta (s)')
ax.grid(True, alpha=0.3)
ax.legend()

# Add title
plt.title('Time Delta to Hamilton\n2025 Chinese GP Sprint Qualifying')

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()

# Print lap times
print(f"\nLap Times:")
for driver_code, driver_info in drivers.items():
    print(f"{driver_info['label']}: {driver_info['lap']['LapTime']}")

# Calculate time differences relative to Hamilton
print(f"\nTime Differences (relative to Hamilton):")
hamilton_time = drivers['HAM']['lap']['LapTime']
for driver_code, driver_info in drivers.items():
    if driver_code != 'HAM':
        time_diff = driver_info['lap']['LapTime'] - hamilton_time
        print(f"{driver_info['label']}: {time_diff}") 