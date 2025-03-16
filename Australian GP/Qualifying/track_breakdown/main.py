"""Track section analysis - who was fastest where
================================================
Plot the track map and color each section by the driver who was fastest there.
"""
import matplotlib.pyplot as plt
import fastf1.plotting
import pandas as pd
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as patches

# Enable FastF1's dark color scheme
fastf1.plotting.setup_mpl(misc_mpl_mods=False, color_scheme='fastf1')

# Load a session and its telemetry data
session = fastf1.get_session(2025, 'Australia', 'Q')
session.load()

# Get the list of all drivers who participated in the session
all_drivers = session.results['Abbreviation'].tolist()
print(f"Found {len(all_drivers)} drivers in the session")

# Get the circuit info for the track map
circuit_info = session.get_circuit_info()
if circuit_info is None:
    print("Circuit info not available. Using fastest lap for track visualization.")
    # We can also construct a track map from the fastest lap's telemetry
    fastest_lap = session.laps.pick_fastest()
    fastest_tel = fastest_lap.get_telemetry()
    track_x, track_y = fastest_tel['X'].values, fastest_tel['Y'].values
else:
    print("Using circuit info for track visualization.")
    track_x, track_y = circuit_info.X, circuit_info.Y

# Function to calculate the distance between two points
def distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Divide the track into segments (we'll use 50-100 segments for a good visualization)
num_segments = 80

# Create arrays to store the segments and their points
segments = []
segment_points = []

# Calculate the total track length using the x, y coordinates
track_length = 0
for i in range(1, len(track_x)):
    track_length += distance(track_x[i-1], track_y[i-1], track_x[i], track_y[i])

# Target length of each segment
segment_target_length = track_length / num_segments

# Create the segments
current_segment = []
current_length = 0

for i in range(1, len(track_x)):
    pt1 = (track_x[i-1], track_y[i-1])
    pt2 = (track_x[i], track_y[i])
    
    segment_length = distance(pt1[0], pt1[1], pt2[0], pt2[1])
    
    if current_segment == []:
        current_segment.append(pt1)
    
    current_segment.append(pt2)
    current_length += segment_length
    
    if current_length >= segment_target_length or i == len(track_x) - 1:
        # Store the segment
        if len(current_segment) >= 2:
            segments.append(current_segment)
            # Store the midpoint of this segment
            mid_idx = len(current_segment) // 2
            segment_points.append(current_segment[mid_idx])
        # Start a new segment but keep the last point as the first point
        current_segment = [pt2]
        current_length = 0

print(f"Divided track into {len(segments)} segments")

# Prepare to collect fastest driver in each segment
segment_fastest_driver = [None] * len(segments)
segment_fastest_speed = [0] * len(segments)
driver_colors = {}

# For each driver, analyze their fastest lap
for driver in all_drivers:
    try:
        # Get the fastest lap for the current driver
        driver_lap = session.laps.pick_drivers(driver).pick_fastest()
        
        if driver_lap.empty:
            print(f"No valid lap found for {driver}")
            continue
            
        # Get telemetry data with x, y coordinates
        driver_tel = driver_lap.get_telemetry()
        
        if driver_tel.empty:
            print(f"No telemetry data for {driver}")
            continue
        
        # Get the team color for this driver
        try:
            driver_colors[driver] = fastf1.plotting.driver_color(driver)
        except:
            driver_colors[driver] = 'gray'
        
        # For each segment of the track, find the speed of this driver
        for i, segment in enumerate(segments):
            # Get midpoint of this segment
            mid_x, mid_y = segment_points[i]
            
            # Find the closest point in the telemetry data
            distances = np.sqrt((driver_tel['X'] - mid_x)**2 + (driver_tel['Y'] - mid_y)**2)
            closest_idx = np.argmin(distances)
            
            # Get the speed at this point
            speed = driver_tel['Speed'].iloc[closest_idx]
            
            # Update if this driver is fastest in this segment
            if speed > segment_fastest_speed[i]:
                segment_fastest_driver[i] = driver
                segment_fastest_speed[i] = speed
        
        print(f"Processed data for {driver}")
    except Exception as e:
        print(f"Error processing data for {driver}: {e}")

# Create the plot
plt.figure(figsize=(16, 9))
ax = plt.gca()

# Create a LineCollection for the track segments
track_segments = []
colors = []

for i, segment in enumerate(segments):
    track_segments.append(segment)
    driver = segment_fastest_driver[i]
    if driver is not None:
        colors.append(driver_colors[driver])
    else:
        colors.append('gray')

# Create the LineCollection
track_collection = LineCollection(track_segments, colors=colors, linewidths=5)
ax.add_collection(track_collection)

# Plot the track direction arrow
try:
    # Calculate direction at a point 20% into the track
    idx = int(len(track_x) * 0.2)
    direction_x = track_x[idx+5] - track_x[idx]
    direction_y = track_y[idx+5] - track_y[idx]
    norm = np.sqrt(direction_x**2 + direction_y**2)
    direction_x, direction_y = direction_x/norm, direction_y/norm
    
    # Create arrow
    arrow_x, arrow_y = track_x[idx], track_y[idx]
    ax.arrow(arrow_x, arrow_y, direction_x*500, direction_y*500, 
             head_width=200, head_length=300, fc='white', ec='white', width=50)
    
    # Add "Direction" text
    text_x = arrow_x + direction_x*700
    text_y = arrow_y + direction_y*700
    ax.text(text_x, text_y, "Race Direction", color='white', 
            ha='center', va='center', fontsize=10, 
            bbox=dict(facecolor='black', alpha=0.7))
except Exception as e:
    print(f"Could not add direction arrow: {e}")

# Add corner numbers if available
try:
    if circuit_info is not None and 'Corners' in circuit_info:
        corners = circuit_info['Corners']
        for corner in corners:
            ax.text(corner['X'], corner['Y'], str(corner['Number']),
                   fontsize=9, ha='center', va='center', color='white',
                   bbox=dict(facecolor='black', alpha=0.7))
except Exception as e:
    print(f"Could not add corner numbers: {e}")

# Create a legend with drivers and their colors
handles = []
labels = []

for driver in sorted(driver_colors.keys()):
    if driver in segment_fastest_driver:  # Only show drivers who were fastest somewhere
        count = segment_fastest_driver.count(driver)
        percent = count / len(segment_fastest_driver) * 100
        
        patch = patches.Patch(color=driver_colors[driver], label=f"{driver} ({count} segments, {percent:.1f}%)")
        handles.append(patch)
        labels.append(f"{driver} ({count} segments, {percent:.1f}%)")

# Sort legend by number of fastest segments
counts = [segment_fastest_driver.count(driver) for driver in sorted(driver_colors.keys()) if driver in segment_fastest_driver]
sorted_idx = np.argsort(counts)[::-1]  # Descending order
handles = [handles[i] for i in sorted_idx]
labels = [labels[i] for i in sorted_idx]

# Add the legend to the plot
ax.legend(handles, labels, loc='upper right', fontsize=10)

# Set the limits and aspect ratio
ax.set_xlim(min(track_x) - 200, max(track_x) + 200)
ax.set_ylim(min(track_y) - 200, max(track_y) + 200)
ax.set_aspect('equal')

# Remove axis labels and ticks
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')

# Set title
plt.title(f"Fastest Drivers by Track Section\n{session.event['EventName']} {session.event.year} Qualifying", 
          fontsize=16, color='white')

# Add a subtitle explaining the visualization
plt.figtext(0.5, 0.01, 
            "Each track segment is colored according to the driver who achieved the highest speed there during their fastest qualifying lap.", 
            ha='center', fontsize=10, color='white')

# Save the figure
plt.savefig(f'Australian_GP_2025_Track_Section_Leaders.png', dpi=300, bbox_inches='tight', facecolor='black')

# Show the plot
plt.tight_layout()
plt.show()

# Create a second visualization - speed heatmap on track
try:
    plt.figure(figsize=(16, 9))
    ax2 = plt.gca()
    
    # Create a LineCollection for the track segments but color by speed
    colors_speed = []
    max_speed = max(segment_fastest_speed)
    min_speed = min(filter(lambda x: x > 0, segment_fastest_speed))
    
    # Create a colormap from blue (slow) to red (fast)
    cmap = plt.cm.get_cmap('coolwarm')
    
    for i, segment in enumerate(segments):
        speed = segment_fastest_speed[i]
        if speed > 0:
            # Normalize speed to [0, 1] range for the colormap
            normalized_speed = (speed - min_speed) / (max_speed - min_speed)
            colors_speed.append(cmap(normalized_speed))
        else:
            colors_speed.append('gray')
    
    # Create the LineCollection
    track_collection_speed = LineCollection(track_segments, colors=colors_speed, linewidths=5)
    ax2.add_collection(track_collection_speed)
    
    # Add corner numbers if available
    try:
        if circuit_info is not None and 'Corners' in circuit_info:
            corners = circuit_info['Corners']
            for corner in corners:
                ax2.text(corner['X'], corner['Y'], str(corner['Number']),
                       fontsize=9, ha='center', va='center', color='white',
                       bbox=dict(facecolor='black', alpha=0.7))
    except Exception as e:
        print(f"Could not add corner numbers to speed map: {e}")
    
    # Set the limits and aspect ratio
    ax2.set_xlim(min(track_x) - 200, max(track_x) + 200)
    ax2.set_ylim(min(track_y) - 200, max(track_y) + 200)
    ax2.set_aspect('equal')
    
    # Remove axis labels and ticks
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xlabel('')
    ax2.set_ylabel('')
    
    # Add a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(min_speed, max_speed))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax2)
    cbar.set_label('Speed (km/h)', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    
    # Set title
    plt.title(f"Speed Heatmap by Track Section\n{session.event['EventName']} {session.event.year} Qualifying", 
              fontsize=16, color='white')
    
    # Add a subtitle explaining the visualization
    plt.figtext(0.5, 0.01, 
                "Track sections are colored by speed: blue for slower sections, red for faster sections.", 
                ha='center', fontsize=10, color='white')
    
    # Save the figure
    plt.savefig(f'Australian_GP_2025_Track_Speed_Heatmap.png', dpi=300, bbox_inches='tight', facecolor='black')
    
    # Show the plot
    plt.tight_layout()
    plt.show()
except Exception as e:
    print(f"Error creating speed heatmap: {e}")

# Optional: Export the segment data to CSV
try:
    import os
    
    # Create output directory
    output_dir = 'f1_data_export'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a DataFrame with segment information
    segment_data = []
    
    for i, segment in enumerate(segments):
        mid_x, mid_y = segment_points[i]
        segment_data.append({
            'SegmentID': i,
            'MidpointX': mid_x,
            'MidpointY': mid_y,
            'FastestDriver': segment_fastest_driver[i],
            'FastestSpeed': segment_fastest_speed[i]
        })
    
    segment_df = pd.DataFrame(segment_data)
    segment_df.to_csv(os.path.join(output_dir, f'Track_Segments_{session.event["EventName"]}_{session.event.year}.csv'), index=False)
    print(f"Exported segment data to CSV")
except Exception as e:
    print(f"Error exporting segment data: {e}")