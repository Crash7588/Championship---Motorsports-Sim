import os
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.colors as mcolors
import csv
import mplcursors

# Define points systems
points_systems = {

    "Formula One World Championship": {
        "points": [10, 8, 6, 5, 4, 3, 2, 1],
        "pole_position": 0,
        "fastest_lap": 0,
        "most_laps_led": 0
    },
    "NASCAR Sprint Cup Series": {
        "points": [185, 170, 165, 160, 155, 150, 146, 142, 138, 134, 130, 127, 124, 121, 118, 115, 112, 109, 106, 103, 100, 97, 94, 91, 88, 85, 82, 79, 76, 73, 70, 67, 64, 61, 58, 55, 52, 49, 46, 43, 40, 37, 34, 31, 28, 25, 20, 15, 10, 8, 6, 4, 2, 1],
        "pole_position": 0,
        "fastest_lap": 0,
        "most_laps_led": 5
    },

    ### Other / Fictional Series

    "Mario Kart 150cc Championship": {
        "points": [15, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1],
        "pole_position": 0,
        "fastest_lap": 0,
        "most_laps_led": 0
    },
    "Vitoline Piston Cup Racing Series": {
        "points": [185, 170, 165, 160, 155, 150, 146, 142, 138, 134, 130, 127, 124, 121, 118, 115, 112, 109, 106, 103, 100, 97, 94, 91, 88, 85, 82, 79, 76, 73, 70, 67, 64, 61, 58, 55, 52, 49, 46, 43, 40, 37, 34, 31, 28, 25, 20, 15, 10, 8, 6, 4, 2, 1],
        "pole_position": 0,
        "fastest_lap": 0,
        "most_laps_led": 0
    },
    "Other Series": {
        "points": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
        "pole_position": 0,
        "fastest_lap": 0,
        "most_laps_led": 0
    }
}

# Configuration to determine if a series has a playoff system
series_playoff_config = {
    'Formula One World Championship': {
        'playoff_enabled': False
    },
    'NASCAR Sprint Cup Series': {
        'playoff_enabled': True,
        'regular_season_races': 26,  # Number of races before playoffs begin
        'playoff_drivers': 12,  # Number of drivers in the playoffs
        'playoff_reset_points': 5000,  # Points reset for playoff drivers
        'playoff_bonus_points_type': "Wins", # Points for either position in standings or wins (Standings/Wins)
        'playoff_bonus_points': 10  # Points awarded for each win / standings position in the regular season
    },

    ### Other / Fictional Series

    'Mario Kart 150cc Championship': {
        'playoff_enabled': False
    },
    'Vitoline Piston Cup Racing Series': {
        'playoff_enabled': True,
        'regular_season_races': 26,  # Number of races before playoffs begin
        'playoff_drivers': 10,  # Number of drivers in the playoffs
        'playoff_reset_points': 4000,  # Points reset for playoff drivers
        'playoff_bonus_points_type': "Standings", # Points for either position in standings or wins (Standings/Wins)
        'playoff_bonus_points': 10  # Points awarded for each win in the regular season
    },
    'Other Series': {
        'playoff_enabled': False
    }
}


# Initialize standings
standings = {}

def apply_points(series_name, race_results, qualifying_results, dnf_drivers, dnq_drivers, fastest_lap_data, most_laps_led_data, discipline):
    points_system = points_systems.get(series_name, points_systems["Other Series"])
    points = points_system.get("points", [])
    pole_position_points = points_system.get("pole_position", 0)
    fastest_lap_points = points_system.get("fastest_lap", 0)
    most_laps_led_points = points_system.get("most_laps_led", 0)

    # Initialize standings for all drivers seen in race or qualifying
    all_drivers = set()
    if race_results:
        for result in race_results:
            all_drivers.add(result["Driver"])
    if qualifying_results:  # Use qualifying_results directly as it's already a list
        for result in qualifying_results:
            all_drivers.add(result["Driver"])
    if dnf_drivers:
        for driver_info in dnf_drivers:
            all_drivers.add(driver_info["Driver"])
    
    all_drivers_dnq = set()
    if dnq_drivers:
        for driver_info in dnq_drivers:
            all_drivers_dnq.add(driver_info["Driver"])

    for driver in all_drivers:
        if driver not in standings:
            if discipline == "StockCar":
                standings[driver] = {"Points": 0, "Wins": 0, "Top 5s": 0, "Top 10s": 0, "Poles": 0, "DNFs": 0, "Races": 0}
            else:
                standings[driver] = {"Points": 0, "Wins": 0, "Podiums": 0, "Poles": 0, "DNFs": 0, "Races": 0}
            standings[driver]["Races"] += 1
        else:
            standings[driver]["Races"] += 1

    for driver in all_drivers_dnq:
        if driver not in standings:
            if discipline == "StockCar":
                standings[driver] = {"Points": 0, "Wins": 0, "Top 5s": 0, "Top 10s": 0, "Poles": 0, "DNFs": 0, "Races": 0}
            else:
                standings[driver] = {"Points": 0, "Wins": 0, "Podiums": 0, "Poles": 0, "DNFs": 0, "Races": 0}

    # Process qualifying results for pole position
    if qualifying_results:
        pole_position_driver = qualifying_results[0].get("Driver")
        if pole_position_driver:
            standings[pole_position_driver]["Points"] += pole_position_points
            standings[pole_position_driver]["Poles"] += 1

    # Append DNF drivers to race results and assign them positions
    if dnf_drivers:
        dnf_position = len(race_results) + 1
        for driver_info in dnf_drivers:
            driver_info["Position"] = dnf_position
            race_results.append(driver_info)
            dnf_position += 1

    # Process race results and DNFs together
    for i, result in enumerate(race_results):
        driver = result["Driver"]
        position = i + 1
        result_points = points[position - 1] if position - 1 < len(points) else 0

        standings[driver]["Points"] += result_points
        if position == 1:
            standings[driver]["Wins"] += 1
        if discipline == "StockCar":
            if position <= 5:
                standings[driver]["Top 5s"] += 1
            if position <= 10:
                standings[driver]["Top 10s"] += 1
        if discipline != "StockCar":
            if position <= 3:
                standings[driver]["Podiums"] += 1

    if dnf_drivers:
        for driver_info in dnf_drivers:
            driver = driver_info["Driver"]
            if driver in standings:
                standings[driver]["DNFs"] += 1

    # Award points for fastest lap
    if fastest_lap_data:
        fastest_lap_driver = fastest_lap_data.get("Driver")
        if fastest_lap_driver:
            standings[fastest_lap_driver]["Points"] += fastest_lap_points

    # Award points for most laps led
    if most_laps_led_data:
        most_laps_led_driver = most_laps_led_data.get("Driver")
        if most_laps_led_driver:
            standings[most_laps_led_driver]["Points"] += most_laps_led_points

def calculate_team_points(standings, team_names):
    team_stats = {}
    for driver, stats in standings.items():
        team_full = team_names.get(driver, "")
        # Split at '-' and take the second part, strip spaces
        if '-' in team_full:
            team = team_full.split('-', 1)[1].strip()
        else:
            team = team_full.strip()
        if team:
            if team not in team_stats:
                team_stats[team] = {k: 0 for k in stats.keys()}
            for k, v in stats.items():
                if k == "Races":
                    # Instead of summing, take max races count among drivers
                    team_stats[team][k] = max(team_stats[team][k], v)
                else:
                    team_stats[team][k] += v
    return team_stats

def reset_for_playoffs(standings, race_index, series_name):
    playoff_config = series_playoff_config.get(series_name, {})
    
    if not playoff_config.get('playoff_enabled', False):
        return standings  # No playoffs, return unchanged standings
    
    # Check if the current race is after the regular season
    if race_index == playoff_config['regular_season_races']:
        # Sort standings by points and take the top drivers
        sorted_standings = sorted(standings.items(), key=lambda x: x[1]['Points'], reverse=True)
        playoff_drivers = sorted_standings[:playoff_config['playoff_drivers']]
        
        # Reset points for playoff drivers and add bonus for wins
        if playoff_config['playoff_bonus_points_type'] == "Wins":
            for driver, stats in playoff_drivers:
                # Base reset points + 10 points per win
                stats['Points'] = playoff_config['playoff_reset_points'] + (stats['Wins'] * 10)
        
        if playoff_config['playoff_bonus_points_type'] == "Standings":
            num_playoff_drivers = playoff_config['playoff_drivers']
            for index, (driver, stats) in enumerate(playoff_drivers):
                # Base reset points + bonus points multiplied by inverted standings position
                stats['Points'] = playoff_config['playoff_reset_points']
                inverted_position = num_playoff_drivers - index
                stats['Points'] += playoff_config['playoff_bonus_points'] * inverted_position
        
        # Return updated standings
        return dict(playoff_drivers)
    
    return standings

def load_results(results_dir, series_name):
    race_results_list = []
    qualifying_results_list = []
    dnf_drivers_list = []
    dnq_drivers_list = []
    fastest_lap_data_list = []
    most_laps_led_data_list = []

    # Iterate through each file in the directory
    for filename in os.listdir(results_dir):
        if filename.endswith(".json") and filename.split(" - ")[0] == series_name:
            try:
                with open(os.path.join(results_dir, filename), 'r') as json_file:
                    results = json.load(json_file)
                    order = results.get("Order")
                    race_results = results.get("Race Results")
                    qualifying_results = results.get("Qualifying Results")
                    dnf_drivers = results.get("DNF Drivers")
                    dnq_drivers = results.get("DNQ Drivers")
                    fastest_lap_data = results.get("Fastest Lap")
                    most_laps_led_data = results.get("Most Laps Led")

                    # Append each set of results to respective lists
                    race_results_list.append(race_results)
                    qualifying_results_list.append(qualifying_results)
                    dnf_drivers_list.append(dnf_drivers)
                    dnq_drivers_list.append(dnq_drivers)
                    fastest_lap_data_list.append(fastest_lap_data)
                    most_laps_led_data_list.append(most_laps_led_data)

            except Exception as e:
                print(f"Error processing file '{os.path.join(results_dir, filename)}': {e}")

    return order, race_results_list, qualifying_results_list, dnf_drivers_list, dnq_drivers_list, fastest_lap_data_list, most_laps_led_data_list

def get_series_attributes_from_csv(series_name, script_directory):
    csv_file_path = os.path.join(script_directory, 'Rules', 'Championship Rules.csv')

    # Check if the "Championship Rules.csv" file exists
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"'Championship Rules.csv' file not found in the specified directory: {csv_file_path}")

    # Read the CSV and search for the matching series_name
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Series'] == series_name:
                discipline = row['Discipline']
                region = row['Region']
                tier = row['Tier']          # Primary / Secondary / Tertiary    |   Premier / Developmental / Invitational
                team_rules = row['Teams']
                chassis_rules = row['Chassis']
                engine_rules = row['Engine']
                practice_sessions = row['Practice Sessions']  # Number of practice sessions
                charter_system = row['Charter']  # Static / Dynamic / None
                charter_slots = row['Charter Slots']  # Number of charter slots available
                retirement_threshold = row['Retirement Threshold']  # Number of retirements before
                return discipline, region, tier, team_rules, chassis_rules, engine_rules, practice_sessions, charter_system, charter_slots, retirement_threshold

    # If no match is found, raise an error
    raise ValueError(f"No match found for series_name: {series_name}")

def plot_driver_performance_heatmap(sorted_standings, race_results_list, dnf_drivers_list, discipline, dnq_drivers_list):
    drivers = [driver for driver, _ in sorted_standings]
    races = len(race_results_list)

    driver_positions = {driver: [np.nan] * races for driver in drivers}

    dnf_list = []  # List of drivers who DNFed in each

    for i, race_results in enumerate(race_results_list):
        for result in race_results:
            driver = result["Driver"]
            position = result["Position"]
            if position > len(race_results):  # Check if position indicates a DNF
                position = len(race_results) + 1
                dnf_list.append(driver)
            if driver in driver_positions:
                driver_positions[driver][i] = position

    # Convert positions to a DataFrame for heatmap
    data = np.array([positions for driver, positions in driver_positions.items()])

    # Define custom color palette
            #  White      Gold       Silver     Bronze     L. Green   L. Blue    D. Blue
    colors = ["#FFFFFF", "#FFECA1", "#E8E8E8", "#DBA851", "#A1EFA9", "#9ABDE9", "#5D87BD"]
    cmap = mcolors.ListedColormap(colors)

    #  L. Purple  Faded Pink
    # "#A77694", #D89C97"

    # Dynamically adjust bounds based on the number of drivers
    if discipline == 'StockCar':
        bounds = [0, 1, 2, 6, 11, 16, 21, 50]
    else:
        bounds = [0, 1, 2, 3, 4, 6, 11, 30]

    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(data, annot=True, fmt=".0f", cmap=cmap, norm=norm, linewidths=.5, linecolor='gray', xticklabels=range(1, races + 1), yticklabels=drivers, annot_kws={"fontsize": 9})

    # Apply pink color for DNQ results and display "DNQ" in the box
    for i, driver in enumerate(drivers):
        for j in range(races):
            if np.isnan(data[i, j]):
                if driver in [dnq_driver["Driver"] for dnq_driver in dnq_drivers_list[j]]:
                    ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True, facecolor='#D89C97', edgecolor='gray', lw=0.5))
                    ax.text(j + 0.5, i + 0.5, 'DNQ', ha='center', va='center', color='black', fontsize=8)

    # Apply a pink tint for DNF results over the existing color
    for i, driver in enumerate(drivers):
        for j in range(races):
            if driver in [dnf_driver["Driver"] for dnf_driver in dnf_drivers_list[j]]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True, facecolor='#A77694', edgecolor='gray', lw=0.5))

    plt.xlabel('Race')
    plt.ylabel('Driver')
    plt.title(f'Driver Standings by Race')
    plt.tight_layout()

    # Save or show the plot
    plt.show()  # Display the plot

def plot_race_by_race_performance(drivers, race_results_list):
    races = len(race_results_list)  # Number of races
    driver_positions = {driver: [] for driver in drivers}

    # Populate race-by-race positions for each driver
    for race_results in race_results_list:
        for driver in drivers:
            position = next((result['Position'] for result in race_results if result['Driver'] == driver), None)
            driver_positions[driver].append(position if position else float('nan'))

    # Plot race-by-race performance for each driver
    plt.figure(figsize=(12, 8))
    lines = []

    # Generate a color palette with Seaborn
    palette = sns.color_palette('hls', len(drivers))  # 'husl', 'pastel', 'dark', etc.

    for i, driver in enumerate(drivers):
        line, = plt.plot(range(1, races + 1), driver_positions[driver], 
                         marker='o', label=driver, 
                         color=palette[i])
        lines.append((line, driver))

    # Add labels, title, and grid
    plt.xlabel('Race')
    plt.ylabel('Position')
    plt.title('Race-by-Race Performance of Drivers')
    plt.gca().invert_yaxis()  # Invert y-axis to make 1st position appear on top
    plt.xticks(range(1, races + 1))
    # Set y-ticks to whole numbers only
    min_pos = int(np.nanmin([pos for positions in driver_positions.values() for pos in positions if not np.isnan(pos)]))
    max_pos = int(np.nanmax([pos for positions in driver_positions.values() for pos in positions if not np.isnan(pos)]))
    plt.yticks(np.arange(min_pos, max_pos + 1, 1))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    # Add interactive highlighting using mplcursors
    cursor = mplcursors.cursor(highlight=True)

    @cursor.connect("add")
    def on_add(sel):
        for line, label in lines:
            if sel.artist == line:
                sel.annotation.set_text(f"Driver: {label}")
                sel.annotation.get_bbox_patch().set_facecolor("yellow")
                sel.annotation.get_bbox_patch().set_alpha(0.8)
                # Bolden the line and change its color to yellow when clicked
                line.set_linewidth(4)
                line.set_color("yellow")
                line.set_zorder(10)  # Bring to front

    @cursor.connect("remove")
    def on_remove(sel):
        for line, label in lines:
            if sel.artist == line:
                # Restore original line width and color when deselected
                line.set_linewidth(2)
                # Restore original color from palette
                line.set_color(palette[drivers.index(label)])
                line.set_zorder(1)

    # Set initial line width and color
    for line, driver in lines:
        line.set_linewidth(2)
        line.set_color(palette[drivers.index(driver)])

    plt.show()

def plot_average_positions(sorted_standings, race_results_list, qualifying_results_list):
    drivers = [driver for driver, _ in sorted_standings]
    drivers.reverse()  # Flip the order of the drivers

    avg_race_positions = {driver: [] for driver in drivers}
    avg_quali_positions = {driver: [] for driver in drivers}

    # Collect race positions
    for race_results in race_results_list:
        for result in race_results:
            driver = result["Driver"]
            position = result["Position"]
            if driver in avg_race_positions:
                avg_race_positions[driver].append(position)

    # Collect qualifying positions
    for qualifying_results in qualifying_results_list:
        for result in qualifying_results:
            driver = result["Driver"]
            position = result["Position"]
            if driver in avg_quali_positions:
                avg_quali_positions[driver].append(position)

    # Calculate average positions
    avg_race_positions = {driver: np.mean(positions) for driver, positions in avg_race_positions.items() if positions}
    avg_quali_positions = {driver: np.mean(positions) for driver, positions in avg_quali_positions.items() if positions}

    # Prepare data for plotting
    race_avgs = [avg_race_positions[driver] for driver in drivers if driver in avg_race_positions]
    quali_avgs = [avg_quali_positions[driver] for driver in drivers if driver in avg_quali_positions]

    plt.figure(figsize=(12, 8))

    # Scatter plot for average positions
    plt.scatter(quali_avgs, race_avgs, color='#3498db', alpha=0.8, edgecolors='black', linewidth=1.2)

    # Annotate driver names with a white background box
    for driver in drivers:
        if driver in avg_quali_positions and driver in avg_race_positions:
            plt.text(avg_quali_positions[driver], avg_race_positions[driver], driver, fontsize=9, ha='center', va='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    plt.xlabel('Average Race Position')
    plt.ylabel('Average Qualifying Position')
    plt.title('Average Race Position vs Average Qualifying Position')
    plt.grid(True, linestyle='--', alpha=0.7)

    # Add a 1:1 line for reference
    min_pos = min(min(quali_avgs), min(race_avgs))
    max_pos = max(max(quali_avgs), max(race_avgs))
    plt.plot([min_pos, max_pos], [min_pos, max_pos], linestyle='--', color='red', alpha=0.5)

    # Customize plot limits for better view
    plt.xlim(1, max_pos + 0.5)
    plt.ylim(1, max_pos + 0.5)

    # Set ticks to display only natural numbers
    plt.xticks(np.arange(int(min_pos), int(max_pos) + 1, step=1))
    plt.yticks(np.arange(int(min_pos), int(max_pos) + 1, step=1))

    plt.tight_layout()

    # Save or show the plot
    plt.show()  # Display the plot

def plot_driver_qualifying_heatmap(sorted_standings, qualifying_results_list, dnq_drivers_list):
    drivers = [driver for driver, _ in sorted_standings]
    races = len(qualifying_results_list)

    driver_positions = {driver: [np.nan] * races for driver in drivers}

    for i, qualifying_results in enumerate(qualifying_results_list):
        for result in qualifying_results:
            driver = result["Driver"]
            position = result["Position"]
            if driver in driver_positions:
                driver_positions[driver][i] = position

    for i, dnq_results in enumerate(dnq_drivers_list):
        for result in dnq_results:
            driver = result["Driver"]
            position = result["Position"]
            if driver in driver_positions:
                driver_positions[driver][i] = position

    # Convert positions to a DataFrame for heatmap
    data = np.array([positions for driver, positions in driver_positions.items()])

    plt.figure(figsize=(12, 8))

    # Use LogNorm to create a logarithmic color scale
    norm = mcolors.LogNorm(vmin=np.nanmin(data), vmax=np.nanmax(data))

    # Create the heatmap with logarithmic color scaling
    sns.heatmap(data, annot=True, fmt=".0f", cmap="viridis_r", norm=norm, linewidths=.5, linecolor='gray',
                xticklabels=range(1, races + 1), yticklabels=drivers, annot_kws={"fontsize": 9})

    plt.xlabel('Race')
    plt.ylabel('Driver')
    plt.title(f'Qualifying by Race')
    plt.tight_layout()

    # Save or show the plot
    plt.show()  # Display the plot

def plot_title_fight_progression(sorted_standings, race_results_list, series_name, qualifying_results=None, fastest_lap_data=None, most_laps_led_data=None):

    # Check if the series uses a playoff system
    playoff_config = series_playoff_config.get(series_name, {})
    playoff_enabled = playoff_config.get('playoff_enabled', False)

    # Extract top 2 drivers from standings
    top_drivers = [driver for driver, _ in sorted_standings[:2]]

    # Calculate points threshold
    if sorted_standings:
        points_leader = sorted_standings[0][1]['Points']  # Points of the driver in 1st place
        threshold = 0.75 * points_leader
    else:
        threshold = 0  # Default threshold if standings are empty

    # Include top 5 drivers and others within the threshold
    selected_drivers = [driver for driver, stats in sorted_standings if stats['Points'] >= threshold or driver in top_drivers]

    # Prepare data for plotting
    races = len(race_results_list)  # Total number of races
    title_fight_progression = [[] for _ in range(len(selected_drivers))]  # Initialize lists for each selected driver

    # Process each race separately and update standings
    current_standings = {driver: {'Points': 0} for driver, _ in sorted_standings}

    for i in range(races):
        points_system = points_systems.get(series_name, points_systems["Other Series"])
        points = points_system.get("points", [])
        race_results = race_results_list[i]
        
        # Reset current race standings before processing
        current_race_standings = {driver: {'Points': 0} for driver, _ in sorted_standings}

        for result in race_results:
            driver = result["Driver"]
            position = result["Position"]
            points = points_system.get("points")[position - 1] if position <= len(points_system.get("points")) else 0

            # Add points for race result
            current_race_standings[driver]['Points'] += points

        # Process qualifying results for pole position
        if qualifying_results:
            pole_position_driver = qualifying_results[0].get("Driver")
            if pole_position_driver:
                current_standings[pole_position_driver]["Points"] += points_system.get("pole_position", 0)
                current_standings[pole_position_driver]["Poles"] += 1

        # Award points for fastest lap
        if fastest_lap_data:
            fastest_lap_driver = fastest_lap_data.get("Driver")
            if fastest_lap_driver:
                current_standings[fastest_lap_driver]["Points"] += points_system.get("fastest_lap", 0)

        # Award points for most laps led
        if most_laps_led_data:
            most_laps_led_driver = most_laps_led_data.get("Driver")
            if most_laps_led_driver:
                current_standings[most_laps_led_driver]["Points"] += points_system.get("most_laps_led", 0)

        # Append current race standings to overall standings for plotting
        for j, (driver, stats) in enumerate(sorted_standings):
            current_standings[driver]['Points'] += current_race_standings[driver]['Points']
            if driver in selected_drivers:
                index = selected_drivers.index(driver)
                title_fight_progression[index].append(current_standings[driver]['Points'])

    # Generate a color palette with Seaborn
    palette = sns.color_palette('muted', len(selected_drivers))  # 'husl', 'pastel', 'dark', etc.

    # Store line references and driver names for interactivity
    lines = []

    # Plotting
    plt.figure(figsize=(10, 12))
    for driver, points in zip(selected_drivers, title_fight_progression):
        line, = plt.plot(range(1, races + 1), points, marker='o', label=driver, color=palette[selected_drivers.index(driver)])
        lines.append((line, driver))

    # If playoffs are enabled, indicate where playoffs begin
    if playoff_enabled:
        plt.axvline(playoff_config['regular_season_races'] + 1, color='red', linestyle='--', label="Playoffs")

    plt.xlabel('Race')
    plt.ylabel('Points')
    plt.title('Title Fight Progression')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(range(1, races + 1))
    plt.tight_layout()

    # Add interactive highlighting using mplcursors
    cursor = mplcursors.cursor(highlight=True)

    # Customize the tooltips to show the driver's name and bolden the line on click
    @cursor.connect("add")
    def on_add(sel):
        for line, label in lines:
            if sel.artist == line:
                sel.annotation.set_text(f"Driver: {label}")
                sel.annotation.get_bbox_patch().set_facecolor("yellow")  # Highlight tooltip background
                sel.annotation.get_bbox_patch().set_alpha(0.8)
                line.set_linewidth(4)
                line.set_color("yellow")
                line.set_zorder(10)  # Bring to front

    @cursor.connect("remove")
    def on_remove(sel):
        for line, label in lines:
            if sel.artist == line:
                line.set_linewidth(2)
                # Restore original color from palette
                line.set_color(palette[selected_drivers.index(label)])
                line.set_zorder(1)

    # Set initial line width and color
    for line, driver in lines:
        line.set_linewidth(2)
        line.set_color(palette[selected_drivers.index(driver)])

    # Save or show the plot
    plt.show()  # Display the plot

def extract_filename_parts(filename):
    series_name = filename
    return series_name

def build_position_count(driver_name, race_results_list):
    # Get all positions the driver has finished
    positions = [
        result["Position"]
        for race in race_results_list
        for result in race
        if result["Driver"] == driver_name
    ]
    # Count how many times they finished in each position
    # Lower positions (1st, 2nd, ...) matter more
    return [-positions.count(pos) for pos in range(1, max(positions)+1)]

def main():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    script_filename = os.path.splitext(os.path.basename(__file__))[0]
    series_name = extract_filename_parts(script_filename)

    results_dir = os.path.join(script_directory, os.pardir, 'Schedules', 'Races')

    order, race_results_list, qualifying_results_list, dnf_drivers_list, dnq_drivers_list, fastest_lap_data_list, most_laps_led_data_list = load_results(results_dir, series_name)

    # Extract parts from the CSV file
    discipline, region, tier, team_rules, chassis_rules, engine_rules, practice_sessions, charter_system, charter_slots, retirement_threshold = get_series_attributes_from_csv(series_name, script_directory)

    if len(race_results_list) == 0:
        print(f"No race results loaded from directory: '{results_dir}'")
        return

    # Initialize a list to hold the race data to be written to JSON
    json_output_data = []

    driver_teams_list = {}  # Dictionary to store the teams for each driver

    # Process each race separately
    for i, (race_results, qualifying_results, dnf_drivers, dnq_drivers, fastest_lap_data, most_laps_led_data) in enumerate(zip(race_results_list, qualifying_results_list, dnf_drivers_list, dnq_drivers_list, fastest_lap_data_list, most_laps_led_data_list)):
        if race_results:
            print(f"\nProcessing Race {i + 1}")
            apply_points(series_name, race_results, qualifying_results, dnf_drivers, dnq_drivers, fastest_lap_data, most_laps_led_data, discipline)
            reset_for_playoffs(standings, i, series_name)

            # Track teams for each driver
            for result in race_results:
                driver = result["Driver"]
                team = result["Team"]
                if driver not in driver_teams_list:
                    driver_teams_list[driver] = set()
                driver_teams_list[driver].add(team)

        else:
            print(f"No race results found for Race {i + 1}")

    print("\n\n\n - - - Final Standings - - - \n")
    sorted_standings = sorted(
        standings.items(),
        key=lambda x: (
            -x[1]["Points"],  # descending points
            min([
                result["Position"]
                for race in race_results_list
                for result in race
                if result["Driver"] == x[0]
            ]),  # ascending best position (1 is best)
            *build_position_count(x[0], race_results_list)  # negative counts, so descending by count
        )
    )

    # Collect team names from all race results
    team_names = {}
    supplier_names = {}

    for qualifying_results in qualifying_results_list:
        if qualifying_results:
            for result in qualifying_results:
                driver = result["Driver"]
                team_name = result["Team"]
                team_names[driver] = team_name  # Store the team name for each driver

                supplier = result["Supplier"]
                supplier_names[driver] = supplier  # Store the supplier name for each driver

    for dnq_drivers in dnq_drivers_list:
        if dnq_drivers:
            for dnq_driver in dnq_drivers:
                driver = dnq_driver["Driver"]
                team_name = dnq_driver["Team"]
                team_names[driver] = team_name  # Store the team name for each driver

                supplier = dnq_driver["Supplier"]
                supplier_names[driver] = supplier  # Store the supplier name for each driver

    # Calculate max lengths for formatting
    max_order_length = len(str(len(sorted_standings)))
    max_name_length = max(len(driver) for driver, _ in sorted_standings)
    max_team_length = max(len(team_names.get(driver, "")) for driver, _ in sorted_standings)

    if discipline == "StockCar":
        # Print headers with fixed-width formatting for StockCar
        print(f"    {'Driver':<{max_name_length}} | {'Team':<{max_team_length}} | "
              f"{'Points':>6} | {'Wins':>4} | {'Top 5s':>7} | {'Top 10s':>8} | {'Poles':>5} | {'DNFs':>4} | {'Races':>5}\n")
    else:
        # Print headers with fixed-width formatting for other disciplines
        print(f"    {'Driver':<{max_name_length}} | {'Team':<{max_team_length}} | "
              f"{'Points':>6} | {'Wins':>4} | {'Podiums':>7} | {'Poles':>5} | {'DNFs':>4} | {'Races':>5}\n")

    # Print standings with team names
    for i, (driver, stats) in enumerate(sorted_standings):
        team_name = team_names.get(driver, "")
        if discipline == "StockCar":
            print(f"{i+1:>{max_order_length}}. {driver:<{max_name_length}} | {team_name:<{max_team_length}} | "
                  f"{stats['Points']:>6} | {stats['Wins']:>4} | {stats['Top 5s']:>7} | {stats['Top 10s']:>8} | "
                  f"{stats['Poles']:>5} | {stats['DNFs']:>4} | {stats['Races']:>5}")
        else:
            print(f"{i+1:>{max_order_length}}. {driver:<{max_name_length}} | {team_name:<{max_team_length}} | "
                  f"{stats['Points']:>6} | {stats['Wins']:>4} | {stats['Podiums']:>7} | {stats['Poles']:>5} | "
                  f"{stats['DNFs']:>4} | {stats['Races']:>5}")

    # Calculate and display Team Standings
    team_standings = calculate_team_points(standings, team_names)
    sorted_team_standings = sorted(team_standings.items(), key=lambda x: x[1]["Points"], reverse=True)

    print("\n\n - - - Team Standings - - - \n")
    max_order_length = len(str(len(sorted_team_standings)))
    max_team_name_length = max(len(team) for team, _ in sorted_team_standings)

    # Get all stat keys from the first team (assumes all teams have same keys)
    stat_keys = list(sorted_team_standings[0][1].keys())
    # Prepare header
    header = f"    {'Team':<{max_team_name_length}} | " + " | ".join(f"{key:>{max(6, len(key))}}" for key in stat_keys)
    print(header)
    print('' * len(header))

    # Print each team's stats in numbered order
    for i, (team, stats) in enumerate(sorted_team_standings):
        row = f"{i+1:>{max_order_length}}. {team:<{max_team_name_length}} | " + " | ".join(f"{stats[key]:>{max(6, len(key))}}" for key in stat_keys)
        print(row)

    # Prepare standings data for JSON export
    for i, (driver, stats) in enumerate(sorted_standings):
        team_name = team_names.get(driver, set())
        if discipline == "StockCar":
            json_output_data.append({
                "Rank": i + 1,
                "Driver": driver,
                "Team": team_name,
                "Points": stats['Points'],
                "Wins": stats['Wins'],
                "Top 5s": stats['Top 5s'],
                "Top 10s": stats['Top 10s'],
                "Poles": stats['Poles'],
                "DNFs": stats['DNFs'],
                "Races": stats['Races']
            })
        else:
            json_output_data.append({
                "Rank": i + 1,
                "Driver": driver,
                "Team": team_name,
                "Points": stats['Points'],
                "Wins": stats['Wins'],
                "Podiums": stats['Podiums'],
                "Poles": stats['Poles'],
                "DNFs": stats['DNFs'],
                "Races": stats['Races']
            })

    # Define the JSON file name based on series name and the last round processed
    most_recent_round = order
    json_filename = f"{series_name} - Round {most_recent_round} Standings.json"
    json_filepath = os.path.join(script_directory, 'Logs', json_filename)

    # Write the standings data to the JSON file
    with open(json_filepath, 'w') as json_file:
        json.dump(json_output_data, json_file, indent=4)

    print(f"Standings saved to {json_filename}")

    # Prepare data for plotting
    drivers = [driver for driver, _ in sorted_standings]
    races = len(race_results_list)  # Total number of races

    # Initialize lists to store points progression after each race
    points_progression = [[] for _ in range(len(sorted_standings))]

    # Process each race separately and update standings
    current_standings = {driver: {'Points': 0} for driver, _ in sorted_standings}

    for i in range(races):
        points_system = points_systems.get(series_name, points_systems["Other Series"])
        points = points_system.get("points", [])
        pole_position_points = points_system.get("pole_position", 0)
        fastest_lap_points = points_system.get("fastest_lap", 0)
        most_laps_led_points = points_system.get("most_laps_led", 0)
        race_results = race_results_list[i]
        
        # Reset current race standings before processing
        current_race_standings = {driver: {'Points': 0} for driver, _ in sorted_standings}

        for result in race_results:
            driver = result["Driver"]
            position = result["Position"]
            points = points_systems[series_name]["points"][position - 1] if position <= len(points_systems[series_name]["points"]) else 0

            # Add points for race result
            current_race_standings[driver]['Points'] += points

        # Process qualifying results for pole position
        if qualifying_results:
            pole_position_driver = qualifying_results[0].get("Driver")
            if pole_position_driver:
                standings[pole_position_driver]["Points"] += pole_position_points
                standings[pole_position_driver]["Poles"] += 1

        # Award points for fastest lap
        if fastest_lap_data:
            fastest_lap_driver = fastest_lap_data.get("Driver")
            if fastest_lap_driver:
                standings[fastest_lap_driver]["Points"] += fastest_lap_points

        # Award points for most laps led
        if most_laps_led_data:
            most_laps_led_driver = most_laps_led_data.get("Driver")
            if most_laps_led_driver:
                standings[most_laps_led_driver]["Points"] += most_laps_led_points

        # Append current race standings to overall standings for plotting
        for j, (driver, stats) in enumerate(sorted_standings):
            current_standings[driver]['Points'] += current_race_standings[driver]['Points']
            points_progression[j].append(current_standings[driver]['Points'])

    plt.figure(figsize=(10, 12))

    # Store line references and driver names for interactivity
    lines = []

    # Generate a color palette with Seaborn
    palette = sns.color_palette('muted', len(drivers))  # 'husl', 'pastel', 'dark', etc.

    # Plot each driver's points progression
    for driver, points in zip(drivers, points_progression):
        line, = plt.plot(range(1, races + 1), points, marker='o',
                        label=driver, color=palette[drivers.index(driver)])
        lines.append((line, driver))

    # Add title and labels
    plt.xlabel('Race')
    plt.ylabel('Points')
    plt.title('Championship Points Progression')

    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(range(1, races + 1))
    plt.tight_layout()

    # Add interactive highlighting using mplcursors
    cursor = mplcursors.cursor(highlight=True)

    # Customize the tooltips to show the driver's name and bolden the line on click
    @cursor.connect("add")
    def on_add(sel):
        for line, label in lines:
            if sel.artist == line:
                sel.annotation.set_text(f"Driver: {label}")
                sel.annotation.get_bbox_patch().set_facecolor("yellow")  # Highlight tooltip background
                sel.annotation.get_bbox_patch().set_alpha(0.8)
                line.set_linewidth(4)
                line.set_color("yellow")
                line.set_zorder(10)  # Bring to front

    @cursor.connect("remove")
    def on_remove(sel):
        for line, label in lines:
            if sel.artist == line:
                line.set_linewidth(2)
                # Restore original color from palette
                line.set_color(palette[drivers.index(label)])
                line.set_zorder(1)

    # Set initial line width and color
    for line, driver in lines:
        line.set_linewidth(2)
        line.set_color(palette[drivers.index(driver)])

    # Show the plot
    plt.show()

    plot_driver_performance_heatmap(sorted_standings, race_results_list, dnf_drivers_list, discipline, dnq_drivers_list)

    plot_driver_qualifying_heatmap(sorted_standings, qualifying_results_list, dnq_drivers_list)

    plot_race_by_race_performance(drivers, race_results_list)

    # Plot and show the graphs
    plot_average_positions(sorted_standings, qualifying_results_list, race_results_list)

    plot_title_fight_progression(sorted_standings, race_results_list, series_name, qualifying_results=None, fastest_lap_data=None, most_laps_led_data=None)

if __name__ == "__main__":
    main()