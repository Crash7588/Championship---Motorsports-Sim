import csv ### look for comments with "DEBUG" to find debug print statements
import random
import os
import time
import json
import math
import keyboard
from collections import defaultdict
from rich.console import Console
from rich.text import Text
from rich.live import Live

class Driver:
    def __init__(self, name, nationality, age, psyche, speed, skill, bravery, fitness, experience, morale, preferred_discipline, preferred_track, style, traits, fame, reputation, funding, personal_sponsors, contract, target, relations, team_name):
        self.name = name
        self.nationality = nationality
        self.age = float(age)
        self.psyche = float(psyche)
        self.speed = float(speed)
        self.skill = float(skill)
        self.bravery = float(bravery)
        self.fitness = float(fitness)
        self.experience = float(experience)
        self.morale = float(morale)
        self.preferred_discipline = preferred_discipline
        self.preferred_track = preferred_track
        self.style = style
        self.traits = traits.split("|")  # Split traits by "|"
        self.fame = float(fame)
        self.reputation = float(reputation)
        self.funding = funding.split("|") # 1k / 10k / 100k / 1m / 10m
        self.personal_sponsors = personal_sponsors
        self.contract = contract
        self.target = int(target)
        self.relations = relations      # Just like for most things, it's Terrible / Poor / Fair / Great / Excellent

        self.team_name = team_name
        self.dnf = ""
        self.fantastic_qualifying = False
        self.fantastic_race = False
        self.shocking_qualifying = False
        self.shocking_race = False

        self.tire_choice = "Medium"
        self.tire_condition = 1  # Tire condition starts at 100%
        self.fuel_amount = 1  # Fuel amount starts at 100%

        self.chassis_setup = 0.5  # Chassis setup starts at 50%
        self.chassis_condition = 1  # Chassis condition starts at 100%
        self.engine_condition = 1  # Engine condition starts at 100%
        self.readiness = 0.5  # Readiness starts at 50%
    
        self.team_confidence = 1  # Team confidence starts at 100%

        self.strategy = "Balanced"  # Balanced / Conservative / Aggressive / Opportunistic strategy

class Team:
    def __init__(self, name, charter, alliance, prestige, color, status, primary_sponsor, commitment, secondary_sponsors, chassis, design, performance, aero, gearbox, suspension, brakes, reliability, characteristics, engineer, supplier, engine, power, engine_reliability, tires, pitcrew, strategist):
        self.name = name
        self.charter = charter
        self.alliance = alliance
        self.prestige = prestige
        self.color = color
        self.status = status.split("|")  # Split traits by "|"
        self.primary_sponsor = primary_sponsor
        self.commitment = commitment        # Format: "Type/Duration/TypeOfDuration" (Type - Title/Primary/Premier)
        self.secondary_sponsors = secondary_sponsors.split("|")
        self.chassis = chassis
        self.design = design
        self.performance = float(performance)
        self.aero = float(aero)
        self.gearbox = float(gearbox)
        self.suspension = float(suspension)
        self.brakes = float(brakes)
        self.reliability = float(reliability)
        self.characteristics = characteristics.split("|")  # Split traits by "|"
        self.engineer = engineer
        self.supplier = supplier
        self.engine = engine
        self.power = float(power)
        self.engine_reliability = float(engine_reliability)
        self.tires = tires
        self.pitcrew = pitcrew
        self.strategist = strategist
        self.drivers = []

    def add_driver(self, driver):
        self.drivers.append(driver)

class Weather:
    def __init__(self, clear_prob, rainy_prob, overcast_prob, hot_prob, stormy_prob):
        self.conditions = ['Clear', 'Rainy', 'Overcast', 'Hot', 'Stormy']
        total_prob = clear_prob + rainy_prob + overcast_prob + hot_prob + stormy_prob
        thresholds = [clear_prob, clear_prob + rainy_prob, clear_prob + rainy_prob + overcast_prob,
                      clear_prob + rainy_prob + overcast_prob + hot_prob]
        
        random_value = random.uniform(0, total_prob)
        if random_value < thresholds[0]:
            self.current_condition = 'Clear'
        elif random_value < thresholds[1]:
            self.current_condition = "Rainy"
        elif random_value < thresholds[2]:
            self.current_condition = "Overcast"
        elif random_value < thresholds[3]:
            self.current_condition = "Hot"
        else:
            self.current_condition = "Stormy"

class MarkovChain:
    def __init__(self, order=2):
        self.order = order
        self.chains_by_type = defaultdict(lambda: defaultdict(list))
        self.inappropriate_end_words = {"a", "an", "and", "the", "where", "why", "with", "of", "for", "to", "how", "from", "what", "that", "just"}
    
    def train(self, text, text_type):
        # Split the text while keeping punctuation to ensure proper sentence boundaries
        words = self._split_text(text)
        
        if len(words) < self.order:
            return
        
        # Create the chains by sliding over 'order' number of words
        for i in range(len(words) - self.order):
            key = tuple(words[i:i + self.order])  # Create a tuple of words for the current state
            self.chains_by_type[text_type][key].append(words[i + self.order])
    
    def generate(self, text_type, length=None, driver_name=None, team_name=None):
        if text_type not in self.chains_by_type:
            return f"No data for event type: {text_type}"
        
        # Set default sentence length if not provided
        if not length:
            length = random.randint(5, 15)  # Dynamic length for more variety
        
        chain = self.chains_by_type[text_type]
        if not chain:
            return "No valid data to generate a sentence."
        
        # Randomly choose a starting key (words)
        current_key = random.choice(list(chain.keys()))
        result = list(current_key)  # Seed the sentence with the first 'order' words
        
        for _ in range(length - self.order):
            if current_key not in chain:
                break
            next_word = random.choice(chain[current_key])
            result.append(next_word)
            
            # Update the key by shifting the window over the result
            current_key = tuple(result[-self.order:])
        
        # Capitalize the first word and ensure placeholders are inserted properly
        result[0] = result[0].capitalize()

        # Check if the last word is in the list of inappropriate words
        while result[-1] in self.inappropriate_end_words:
            next_key = tuple(result[-self.order:])  # Get the latest 'order' number of words
            if next_key in chain:
                result.append(random.choice(chain[next_key]))
            else:
                break  # Break if no further valid next word exists
        
        final_sentence = ' '.join(result)
        
        # Ensure proper sentence ending punctuation
        final_sentence = self._end_with_punctuation(final_sentence)
        
        # Replace placeholders for driver_name and team_name dynamically
        if driver_name and team_name:
            final_sentence = final_sentence.replace("{driver_name}", driver_name)
            final_sentence = final_sentence.replace("{team_name}", team_name)
        
        return final_sentence
    
    def load_from_csv(self, script_directory, delimiter='|'):
        csv_file = os.path.join(script_directory, "Data", "Text.csv")
        
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"Interviews.csv not found at {csv_file}")
        
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=delimiter)  # Set custom delimiter
            for row in reader:
                text = row['Text']
                text_type = row['Type']
                self.train(text, text_type)
    
    def _split_text(self, text):
        # This will treat punctuation like '.', '!', and '?' as separate tokens
        return text.replace('.', ' .').replace(',', ',').replace(';', ';').replace('!', ' !').replace('…', ' …').replace('?', ' ?').split()
    
    def _end_with_punctuation(self, sentence):
        # Remove trailing spaces
        sentence = sentence.rstrip()
        # If sentence is empty, just return a period
        if not sentence:
            return '.'
        # If ends with a comma or semicolon, replace with end punctuation
        if sentence[-1] in ",;":
            choices = ['.', '.', '.', '!', '!', '…', '…', '?']
            sentence = sentence[:-1]
            return sentence + random.choice(choices)
        # If ends with multiple punctuation marks (e.g., '!?'), reduce to one
        while len(sentence) > 1 and sentence[-1] in ".!…?," and sentence[-2] in ".!…?,":
            sentence = sentence[:-1]
        # If not ending with a valid end punctuation, add one
        if sentence[-1] not in ".!…?":
            choices = ['.', '.', '.', '!', '!', '…', '…', '?']
            return sentence + random.choice(choices)
        # If ends with valid punctuation, return as is
        return sentence

def simulate_weather(clear_prob, rainy_prob, overcast_prob, hot_prob, stormy_prob):
    weather = Weather(clear_prob, rainy_prob, overcast_prob, hot_prob, stormy_prob)
    return weather.current_condition

def weather_modifier(weather_condition, driver, team):
    if weather_condition == 'Rainy':
        team.performance *= 0.9
        team.power *= 0.9

        if all(trait not in driver.traits for trait in ['WetWeatherSpecialist']):
            driver.speed *= 0.95
            driver.skill *= 0.95

    elif weather_condition == 'Overcast':
        team.reliability *= 1.025

    elif weather_condition == 'Hot':
        driver.skill *= 0.975
        team.reliability *= 0.975

    elif weather_condition == 'Stormy':
        team.performance *= 0.75
        team.power *= 0.75

        if all(trait not in driver.traits for trait in ['WetWeatherSpecialist']):
            driver.speed *= 0.9
            driver.skill *= 0.9

def circuit_type_modifier(circuit_type, driver, team):
    if circuit_type == 'Grand Prix':
        if driver.preferred_track not in ['Road', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['PoorAtRoadCourses']):
            driver.speed *= 0.85
            driver.skill *= 0.85

    if circuit_type == 'Road Course':
        if driver.preferred_track not in ['Road', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['PoorAtRoadCourses']):
            driver.speed *= 0.85
            driver.skill *= 0.85

    if circuit_type == 'Street Track':
        if driver.preferred_track not in ['Road', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['StreetTrackSpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1
        
        if any(characteristic in team.characteristics for characteristic in ['StreetTrackSpecialist']):
            team.performance *= 1.1
            team.power *= 1.1

        if any(trait in driver.traits for trait in ['PoorAtRoadCourses']):
            driver.speed *= 0.85
            driver.skill *= 0.85

    if circuit_type == 'Short Track':
        if driver.preferred_track not in ['Oval', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['ShortTrackSpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1

        if any(characteristic in team.characteristics for characteristic in ['ShortTrackSpecialist']):
            team.performance *= 1.1
            team.power *= 1.1
    
    if circuit_type == 'Mile Oval':
        if driver.preferred_track not in ['Oval', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['MileOvalSpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1

        if any(characteristic in team.characteristics for characteristic in ['MileOvalSpecialist']):
            team.performance *= 1.1
            team.power *= 1.1

    if circuit_type == 'Speedway':
        if driver.preferred_track not in ['Oval', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['SpeedwaySpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1

        if any(characteristic in team.characteristics for characteristic in ['SpeedwaySpecialist']):
            team.performance *= 1.1
            team.power *= 1.1

    if circuit_type == 'Superspeedway':
        if driver.preferred_track not in ['Oval', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['SuperspeedwaySpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1

        if any(characteristic in team.characteristics for characteristic in ['SuperspeedwaySpecialist']):
            team.performance *= 1.1
            team.power *= 1.1

def discipline_modifier(discipline, driver):

    if discipline == 'OpenWheel':
        if driver.preferred_discipline not in ['OpenWheel', 'Any']:
            driver.speed *= 0.65
            driver.skill *= 0.65

            if any(trait in driver.traits for trait in ['Adaptive']):
                driver.speed *= 1.15
                driver.skill *= 1.15

    if discipline == 'Touring':
        if driver.preferred_discipline not in ['Touring', 'Any']:
            driver.speed *= 0.85
            driver.skill *= 0.85

            if any(trait in driver.traits for trait in ['Adaptive']):
                driver.speed *= 1.05
                driver.skill *= 1.05

    if discipline == 'StockCar':
        if driver.preferred_discipline not in ['StockCar', 'Any']:
            driver.speed *= 0.65
            driver.skill *= 0.65

            if any(trait in driver.traits for trait in ['Adaptive']):
                driver.speed *= 1.15
                driver.skill *= 1.15

    if discipline == 'Endurance':
        if driver.preferred_discipline not in ['Endurance', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

            if any(trait in driver.traits for trait in ['Adaptive']):
                driver.speed *= 1.05
                driver.skill *= 1.05

def normalizer(driver, team):
    # Normalize driver attributes (speed and skill) to reduce the gap between low and high values
    driver.speed = 50 + (driver.speed - 50) * 0.5  # Reduce the deviation from the average
    driver.skill = 50 + (driver.skill - 50) * 0.5  # Reduce the deviation from the average

    # Normalize team attributes (performance and power) with a smaller gap
    team.performance = 70 + (team.performance - 70) * 0.5  # Reduce the deviation from the average
    team.power = 35 + (team.power - 35) * 0.5  # Reduce the deviation from the average

def morale_modifier(driver):
    if driver.morale > 0.8:
        driver.speed *= 1 + (driver.morale - 0.75) * 0.25
        driver.skill *= 1 + (driver.morale - 0.75) * 0.25
        driver.team_confidence *= 1 + (driver.morale - 0.75) * 0.25
    elif driver.morale < 0.5:
        driver.speed *= 1 - (0.75 - driver.morale) * 0.25
        driver.skill *= 1 - (0.75 - driver.morale) * 0.25
        driver.team_confidence *= 1 - (0.75 - driver.morale) * 0.25

def track_difficulty_modifier(difficulty, driver):
    penalty_factor = (difficulty / 2.5) 

    # Apply more penalty if stat is low
    driver.speed *= 1 - ((1 - (driver.speed / 100)) * penalty_factor) 

    # Skill penalty increased for lower experience
    experience_penalty = 1 + (1 - driver.experience)

    driver.skill *= 1 - ((1 - (driver.skill / 100)) * penalty_factor * experience_penalty)

def style_vs_design_modifier(driver, team):
    if driver.style == "Oversteer" and team.design == "Understeer":
        driver.speed *= random.uniform(0.85, 0.95)
        driver.skill *= random.uniform(0.875, 0.975)

    if driver.style == "Oversteer" and team.design == "Balanced":
        driver.speed *= random.uniform(0.925, 0.975)
        driver.skill *= random.uniform(0.925, 0.975)

    if driver.style == "Understeer" and team.design == "Oversteer":
        driver.speed *= random.uniform(0.85, 0.95)
        driver.skill *= random.uniform(0.825, 0.925)

    if driver.style == "Understeer" and team.design == "Balanced":
        driver.speed *= random.uniform(0.925, 0.975)
        driver.skill *= random.uniform(0.925, 0.975)

    if driver.style == "Balanced" and team.design == "Oversteer":
        driver.speed *= random.uniform(0.925, 0.975)
        driver.skill *= random.uniform(0.925, 0.975)

    if driver.style == "Balanced" and team.design == "Understeer":
        driver.speed *= random.uniform(0.925, 0.975)
        driver.skill *= random.uniform(0.925, 0.975)

    if driver.style == "None":
        driver.speed *= random.uniform(0.9, 0.975)
        driver.skill *= random.uniform(0.9, 0.975)

    if team.design == "None":
        driver.speed *= random.uniform(0.9, 0.975)
        driver.skill *= random.uniform(0.9, 0.975)

def trait_modifier(driver, sorted_schedule, race):
    if any(trait in driver.traits for trait in ['Inconsistent']):
        random_value = random.uniform(0, 1)
        if random_value < 0.5:
            driver.speed *= random.uniform(0.8, 0.9)
            driver.skill *= random.uniform(0.8, 0.9)
        elif random_value > 0.85:
            driver.speed *= random.uniform(1.05, 1.1)
            driver.skill *= random.uniform(1.05, 1.1)
        else:
            pass

    if any(trait in driver.traits for trait in ['EarlySeasonPeak']):
        current_race_order = int(race['Order'])
        if current_race_order <= len(sorted_schedule) // 2:
            driver.speed *= random.uniform(1, 1.05)
            driver.skill *= random.uniform(1, 1.05)
        else:
            driver.speed *= random.uniform(0.9, 1)
            driver.skill *= random.uniform(0.9, 1)

    if any(trait in driver.traits for trait in ['LateSeasonPeak']):
        current_race_order = int(race['Order'])
        if current_race_order >= len(sorted_schedule) // 2:
            driver.speed *= random.uniform(1, 1.05)
            driver.skill *= random.uniform(1, 1.05)
        else:
            driver.speed *= random.uniform(0.9, 1)
            driver.skill *= random.uniform(0.9, 1)

    if any(trait in driver.traits for trait in ['Overwhelmed']):
        random_value = random.uniform(0, 1)
        if random_value < 0.5:
            driver.speed *= random.uniform(0.825, 0.9) # Slower due to hesitation
            driver.skill *= random.uniform(0.9, 0.975)
        elif random_value > 0.75:
            driver.speed *= random.uniform(0.9, 0.975)
            driver.skill *= random.uniform(0.825, 0.9) # Decreased skill under pressure
        else:
            pass

def race_trait_modifier(driver, starting_position, qualifying_results, track_characteristics, iteration):
    num_drivers = len(qualifying_results)
    bottom_25 = int(num_drivers * 0.75)

    if iteration == 0:
        if starting_position > bottom_25:
            if any(trait in driver.traits for trait in ['Heroic']):
                driver.speed *= 1.05
                driver.skill *= 1.05
            if any(trait in driver.traits for trait in ['Yielding']):
                driver.speed *= 0.9
                driver.skill *= 0.9

        if starting_position == 0:
            if any(trait in driver.traits for trait in ['PoorFromPole']):
                driver.speed *= 0.9
                driver.skill *= 0.9
            if any(trait in driver.traits for trait in ['GreatFromPole']):
                driver.speed *= 1.05
                driver.skill *= 1.05

    if iteration == 0:
        if any(t_characteristic in track_characteristics for t_characteristic in ['Prestigious']):
            random_value = random.uniform(0, 1)
            if random_value < 0.15:
                driver.skill *= random.uniform(0.95, 0.975)

def chassis_performance_and_power_modifier(team, track_speed):
    if track_speed == "Low":
        base = 50
        deviation = team.power - base
        scaled_deviation = deviation * (deviation / 100)  # nonlinear reduction
        team.power = base + deviation - scaled_deviation
    if track_speed == "High":
        base = 50
        deviation = team.power - base
        scaled_boost = deviation * (deviation / 100)  # nonlinear boost
        team.power = base + deviation + scaled_boost

    team.performance += team.aero * 0.1 # maybe do something so that depending on the team.engineer each component is more or less effective
    team.performance += team.gearbox * 0.1
    team.performance += team.suspension * 0.1
    team.performance += team.brakes * 0.1

def simulate_practice(driver, team):
    setup_knowledge = 0.35
    driver_knowledge = 0.35

    setup_knowledge *= (team.aero / 100)
    setup_knowledge *= (team.gearbox / 100)
    setup_knowledge *= (team.suspension / 100)
    setup_knowledge *= (team.brakes / 100)

    setup_knowledge *= driver.team_confidence

    driver_knowledge *= (team.aero / 100)
    driver_knowledge *= (team.gearbox / 100)
    driver_knowledge *= (team.suspension / 100)
    driver_knowledge *= (team.brakes / 100)

    driver_knowledge *= driver.team_confidence
    driver_knowledge *= driver.experience

    if team.engineer == "Terrible":
        if random.uniform(0, 1) > 0.5:
            setup_knowledge += random.uniform(0.025, 0.125)
            driver_knowledge += random.uniform(0.025, 0.125)
        else:
            setup_knowledge *= random.uniform(0.9, 1)
            driver_knowledge *= random.uniform(0.9, 1)

    if team.engineer == "Poor":
        if random.uniform(0, 1) > 0.4:
            setup_knowledge += random.uniform(0.05, 0.15)
            driver_knowledge += random.uniform(0.05, 0.15)
        else:
            setup_knowledge *= random.uniform(0.9, 1)
            driver_knowledge *= random.uniform(0.9, 1)

    if team.engineer == "Fair":
        if random.uniform(0, 1) > 0.3:
            setup_knowledge += random.uniform(0.075, 0.175)
            driver_knowledge += random.uniform(0.075, 0.175)
        else:
            setup_knowledge *= random.uniform(0.9, 1)
            driver_knowledge *= random.uniform(0.9, 1)

    if team.engineer == "Great":
        if random.uniform(0, 1) > 0.2:
            setup_knowledge += random.uniform(0.1, 0.2)
            driver_knowledge += random.uniform(0.1, 0.2)
        else:
            setup_knowledge *= random.uniform(0.9, 1)
            driver_knowledge *= random.uniform(0.9, 1)

    if team.engineer == "Excellent":
        if random.uniform(0, 1) > 0.1:
            setup_knowledge += random.uniform(0.15, 0.25)
            driver_knowledge += random.uniform(0.15, 0.25)
        else:
            setup_knowledge *= random.uniform(0.9, 1)
            driver_knowledge *= random.uniform(0.9, 1)

    return setup_knowledge, driver_knowledge

def simulate_qualifying(team, weather_condition, discipline, event, grid_size, circuit_type, series_name, script_directory, track_speed, track_characteristics, sorted_schedule, race, practice_sessions, difficulty):
    standings_data = read_standings_data(series_name, script_directory, discipline)

    # List to store qualifying results for all drivers in the team
    qualifying_results = []

    # Create a copy of the drivers list to iterate over
    drivers_copy = team.drivers[:]

    for driver in drivers_copy:

        # Check and remove drivers based on contract status and probabilities

        if any(status in team.status for status in ['Insecure']) and standings_data:
            # Calculate the number of races missed by the driver
            entry_standings = standings_data.get("entrants_standings", [])
            current_race_order = int(race['Order'])
            missed_races = 0
            for entry in entry_standings:
                if entry["Entrant"] == team.name:
                    missed_races = current_race_order - entry["Races"]

            # Calculate the threshold based on missed races
            threshold = 0.1 + (0.1 * (missed_races / 2))

            if event != 'Premier' and random.uniform(0, 1) < threshold:
                team.drivers.remove(driver)
                continue

        if any(status in team.status for status in ['Limited']) and event != 'Premier' and random.uniform(0, 1) < 0.66:
            team.drivers.remove(driver)
            continue

        if any(status in team.status for status in ['Guest']) and random.uniform(0, 1) < 0.925:
            team.drivers.remove(driver)
            continue

        # For Premier contract, ensure they participate in "Premier" events
        if any(status in team.status for status in ['Premier']) and event != 'Premier' and random.uniform(0, 1) < 0.975:
            continue

        # Apply modifiers. Effects are applied to the race def as well
        weather_modifier(weather_condition, driver, team)
        circuit_type_modifier(circuit_type, driver, team)
        discipline_modifier(discipline, driver)
        style_vs_design_modifier(driver, team)
        trait_modifier(driver, sorted_schedule, race)
        track_difficulty_modifier(difficulty, driver)

        morale_modifier(driver)

        # normalizer(driver, team)

        for _ in range(int(practice_sessions)):
            setup_knowledge, driver_knowledge = simulate_practice(driver, team)
            if setup_knowledge:  # Ensure the result is valid
            # Accumulate the practice results using the chassis_setup attribute
                driver.chassis_setup = min(driver.chassis_setup + setup_knowledge, 1)  # Cap at 1
                driver.readiness = min(driver.readiness + driver_knowledge, 1)  # Cap at 1
        
        # DEBUG print(f"Driver {driver.name} Setup Knowledge: {driver.chassis_setup}, Driver Knowledge: {driver.readiness}")
        
        team.performance *= driver.chassis_setup
        team.power *= driver.chassis_setup

        driver.speed *= driver.readiness
        driver.skill *= driver.readiness

        driver.fantastic_qualifying = False  # Reset fantastic_qualifying attribute
        driver.shocking_qualifying = False  # Reset shocking_qualifying attribute
        driver.fantastic_race = False
        driver.shocking_race = False

        randomness = random.uniform(-0.05, 0.05)
        fantastic_chance = 0.0075
        shocking_chance = 0.015

        fantastic_chance += (driver.speed / 10000)
        shocking_chance += ((100 - driver.speed) / 10000)

        if any(status in team.status for status in ['R/D']) and random.uniform(0, 1) < 0.5:
            fantastic_chance *= 1.1
            shocking_chance *= 1.25

        if team.strategist == "Terrible":
            fantastic_chance *= random.uniform(0.875, 0.925)
            shocking_chance *= random.uniform(1.075, 1.125)
        elif team.strategist == "Poor":
            fantastic_chance *= random.uniform(0.925, 0.975)
            shocking_chance *= random.uniform(1.025, 1.075)
        elif team.strategist == "Great":
            fantastic_chance *= random.uniform(1.025, 1.075)
            shocking_chance *= random.uniform(0.925, 0.975)
        elif team.strategist == "Excellent":
            fantastic_chance *= random.uniform(1.075, 1.125)
            shocking_chance *= random.uniform(0.875, 0.925)

        if weather_condition == 'Clear':
            randomness = random.uniform(-0.05, 0.05)
            if random.uniform(0, 1) < fantastic_chance:
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < shocking_chance:
                driver.shocking_qualifying = True

        elif weather_condition == 'Rainy':
            randomness = random.uniform(-0.15, 0.15)
            if random.uniform(0, 1) < (fantastic_chance * 2.5):
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < (shocking_chance * 2.5):
                driver.shocking_qualifying = True

        elif weather_condition == 'Overcast':
            if random.uniform(0, 1) < fantastic_chance:
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < (shocking_chance * 0.5):
                driver.shocking_qualifying = True

        elif weather_condition == 'Hot':
            if random.uniform(0, 1) < (fantastic_chance * 0.5):
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < (shocking_chance * 1.5):
                driver.shocking_qualifying = True

        else:
            randomness = random.uniform(-0.2, 0.2)
            if random.uniform(0, 1) < (fantastic_chance * 5):
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < (shocking_chance * 5):
                driver.shocking_qualifying = True
        
        # Store the original skill value
        original_skill = driver.skill
        original_speed = driver.speed

        special_modifier = 1
        if driver.fantastic_qualifying:
            # DEBUG print(f"{driver.name} Fantastic Qualifying")
            if random.uniform(0, 1) < 0.75:
                special_modifier *= 1.25
                if random.uniform(0, 1) < 0.5:
                    # DEBUG print(f"{driver.name} Even More Fantastic (Q)")
                    special_modifier *= 1.25
                    if random.uniform(0, 1) < 0.25:
                        # DEBUG print(f"{driver.name} EVEN MORE FANTASTIC")
                        special_modifier *= 1.25
            else:
                special_modifier *= 1.25

        if driver.shocking_qualifying:
            # DEBUG print(f"{driver.name} Shocking Qualifying")
            if random.uniform(0, 1) < 0.75:
                special_modifier *= 0.75
                if random.uniform(0, 1) < 0.5:
                    # DEBUG print(f"{driver.name} Even More Shocking (Q)")
                    special_modifier *= 0.75
                    if random.uniform(0, 1) < 0.25:
                        # DEBUG print(f"{driver.name} EVEN MORE SHOCKING")
                        special_modifier *= 0.75
            else:
                special_modifier *= 0.75

        if circuit_type in ['Superspeedway']:
            randomness *= 1.25
        elif circuit_type in ['Speedway']:
            randomness *= 1.2
        elif circuit_type in ['Mile Oval']:
            randomness *= 1.15
        elif circuit_type in ['Short Track']:
            randomness *= 1.1

        if discipline == 'StockCar':
            randomness *= 1.15

        random_factor = 1 + (randomness * 2)

        if any(trait in driver.traits for trait in ['QualifyingSpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1

        qualifying_result = (((driver.speed + (driver.skill / 2) + (driver.bravery / 10)) * 0.75) * special_modifier) + team.performance + team.power
        qualifying_result *= random_factor
        qualifying_results.append(qualifying_result)

        # Reset the driver's skill to its original value
        driver.skill = original_skill
        driver.speed = original_speed

    if not qualifying_results:  # If no drivers qualified, return None
        return None

    # Sort the qualifying results in descending order
    qualifying_results.sort(reverse=True)

    # Drivers who qualify outside of the grid size DNQ
    qualified_drivers = qualifying_results[:grid_size]
    dnq_drivers = qualifying_results[grid_size:]

    return qualified_drivers, dnq_drivers

def simulate_race(driver, team, starting_position, weather_condition, discipline, circuit_type, qualifying_results, sorted_qualifying_results, track_characteristics, iteration, iterations):
    # Reset qualifying attributes for the race simulation
    driver.fantastic_qualifying = False  # Reset fantastic_qualifying attribute
    driver.shocking_qualifying = False  # Reset shocking_qualifying attribute

    original_performance = team.performance
    original_power = team.power

    adjusted_tire_effect = 1 - (1 - driver.tire_condition) * 0.25
    team.performance *= adjusted_tire_effect
    team.power *= adjusted_tire_effect

    race_trait_modifier(driver, starting_position, qualifying_results, track_characteristics, iteration)

    pitstop = 0

    if driver.tire_condition < 0.5:
        pitstop = simulate_pitstop(team)
        # DEBUG print(f"Iteration {iteration + 1} | {driver.name} Pitstop: {pitstop}")
        driver.tire_condition = 1.0  # Reset tire condition after pitstop

    if not team.drivers:
        # If there are no drivers in the team, return a performance score of 0
        return 0

    if simulate_crash(driver, iterations) == "Crash":
        driver.dnf = "Crash"
        # If the driver crashes, return a performance score of 0
        return 0

    if simulate_retirement(driver, team, starting_position, qualifying_results, iteration, iterations) == "Retirement":
        driver.dnf = "Retirement"
        # If the driver encounters a mechanical issue, return a performance score of 0
        return 0

    # Store the original skill value
    original_skill = driver.skill
    original_speed = driver.speed

    # Progressive fitness impact
    progress_factor = iteration / iterations  # from 0.0 (start) to almost 1.0 (end)
    fitness_effect = 1 - (1 - driver.fitness) * progress_factor
    driver.skill *= fitness_effect
    driver.speed *= fitness_effect

    randomness = random.uniform(-0.05, 0.05)
    fantastic_chance = 0.0075
    shocking_chance = 0.015

    race_strategy = 0

    if any(t_characteristic in track_characteristics for t_characteristic in ['Chaotic']):
        fantastic_chance *= 1.1
        shocking_chance *= 1.1

    if any(t_characteristic in track_characteristics for t_characteristic in ['Tame']):
        fantastic_chance *= 0.9
        shocking_chance *= 0.9

    fantastic_chance += (driver.skill / 10000) - ((1 - team.reliability) / 1000)
    shocking_chance += ((100 - driver.skill) / 10000) + ((1 - team.reliability) / 1000)

    if team.strategist == "Terrible":
        fantastic_chance *= random.uniform(0.875, 0.925)
        shocking_chance *= random.uniform(1.075, 1.125)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.9:
            race_strategy = random.uniform(0.1, 0.2)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.1
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.9
        elif strategy_value < 0.3:
            race_strategy = random.uniform(-0.3, -0.2)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1
        else:
            race_strategy = random.uniform(-0.2, -0.15)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1

    if team.strategist == "Poor":
        fantastic_chance *= random.uniform(0.925, 0.975)
        shocking_chance *= random.uniform(1.025, 1.075)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.9:
            race_strategy = random.uniform(0.15, 0.25)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.1
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.9
        elif strategy_value < 0.3:
            race_strategy = random.uniform(-0.25, -0.15)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1
        else:
            race_strategy = -random.uniform(-0.15, -0.05)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1

    if team.strategist == "Fair":
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.75:
            race_strategy = random.uniform(0.18, 0.28)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.1
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.9
        elif strategy_value < 0.25:
            race_strategy = random.uniform(-0.22, -0.12)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1
        else:
            race_strategy = -random.uniform(-0.12, -0.02)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1

    if team.strategist == "Great":
        fantastic_chance *= random.uniform(1.025, 1.075)
        shocking_chance *= random.uniform(0.925, 0.975)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.7:
            race_strategy = random.uniform(0.2, 0.3)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.1
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.9
        elif strategy_value < 0.1:
            race_strategy = random.uniform(-0.2, -0.1)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1
        else:
            race_strategy = random.uniform(-0.1, 0)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1

    if team.strategist == "Excellent":
        fantastic_chance *= random.uniform(1.075, 1.125)
        shocking_chance *= random.uniform(0.875, 0.925)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.7:
            race_strategy = random.uniform(0.25, 0.35)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.1
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.9
        elif strategy_value < 0.1:
            race_strategy = random.uniform(-0.15, -0.05)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1
        else:
            race_strategy = random.uniform(-0.05, 0)
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.9
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.1

    if weather_condition == 'Clear':
        randomness = random.uniform(-0.05, 0.05)
        if random.uniform(0, 1) < fantastic_chance:  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < shocking_chance:  # Chance for shocking race
            driver.shocking_race = True

    elif weather_condition == 'Rainy':
        race_strategy *= 1.25
        randomness = random.uniform(-0.15, 0.15)
        if random.uniform(0, 1) < (fantastic_chance * 2.5):  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < (shocking_chance * 2.5):  # Chance for shocking race
            driver.shocking_race = True

    elif weather_condition == 'Overcast':
        if random.uniform(0, 1) < fantastic_chance:  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < (shocking_chance * 0.5):  # Chance for shocking race
            driver.shocking_race = True

    elif weather_condition == 'Hot':
        if random.uniform(0, 1) < (fantastic_chance * 0.5):  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < (shocking_chance * 1.5):  # Chance for shocking race
            driver.shocking_race = True

    else:
        race_strategy *= 1.5
        randomness = random.uniform(-0.2, 0.2)
        if random.uniform(0, 1) < (fantastic_chance * 5):  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < (shocking_chance * 5):  # Chance for shocking race
            driver.shocking_race = True

    special_modifier = 1
    if driver.fantastic_race:
        # DEBUG print(f"{driver.name} Fantastic Race")
        if random.uniform(0, 1) < 0.75:
            special_modifier *= 1.25
            if random.uniform(0, 1) < 0.5:
                # DEBUG print(f"{driver.name} Even More Fantastic Race")
                special_modifier *= 1.25
                if random.uniform(0, 1) < 0.25:
                    # DEBUG print(f"{driver.name} EVEN MORE FANTASTIC RACE")
                    special_modifier *= 1.25
        else:
            special_modifier *= 1.25

    if driver.shocking_race:
        # DEBUG print(f"{driver.name} Shocking Race")
        if random.uniform(0, 1) < 0.75:
            special_modifier *= 0.75
            if random.uniform(0, 1) < 0.5:
                # DEBUG print(f"{driver.name} Even More Shocking Race")
                special_modifier *= 0.75
                if random.uniform(0, 1) < 0.25:
                    # DEBUG print(f"{driver.name} EVEN MORE SHOCKING RACE")
                    special_modifier *= 0.75
        else:
            special_modifier *= 0.75
    
    position_factor = 1

    # Calculate penalty factor / randomness based on starting position
    # Reduce the effects of position_factor by lowering the multipliers
    if circuit_type in ['Superspeedway']:
        position_factor = 1 / (1 + (starting_position - 1) * 0.07)
        randomness *= 1.25
    elif circuit_type in ['Speedway']:
        position_factor = 1 / (1 + (starting_position - 1) * 0.08)
        randomness *= 1.2
    elif circuit_type in ['Mile Oval']:
        position_factor = 1 / (1 + (starting_position - 1) * 0.09)
        randomness *= 1.15
    elif circuit_type in ['Short Track']:
        position_factor = 1 / (1 + (starting_position - 1) * 0.11)
        randomness *= 1.1
    elif circuit_type in ['Road Course', 'Grand Prix']:
        position_factor = 1 / (1 + (starting_position - 1) * 0.15)
    elif circuit_type in ['Street Track']:
        position_factor = 1 / (1 + (starting_position - 1) * 0.18)
    else:
        position_factor = 1 / (1 + (starting_position - 1) * 0.13)
    
    if discipline == 'StockCar':
        randomness *= 1.15
    
    if any(t_characteristic in track_characteristics for t_characteristic in ['Tame']):
        randomness *= 0.95
    
    if any(t_characteristic in track_characteristics for t_characteristic in ['Chaotic']):
        randomness *= 1.05

    if iteration == 0:
        if any(trait in driver.traits for trait in ['QualifyingSpecialist']):
            driver.speed *= 0.9
            driver.skill *= 0.9
    
    random_factor = 1 + (randomness * 2)

    strategy_factor = 1 + race_strategy / iterations

    race_result = ((((driver.speed / 2) + driver.skill) * 0.75) * special_modifier) + team.performance + team.power
    race_result *= strategy_factor # Apply strategy factor
    race_result *= random_factor # Apply randomness
    race_result *= position_factor # Better starting position gives a performance boost
    if pitstop != 0:
        race_result *= pitstop

    # Reset the driver's skill to its original value
    driver.skill = original_skill
    driver.speed = original_speed

    team.performance = original_performance
    team.power = original_power

    driver.fantastic_race = False
    driver.shocking_race = False

    driver.tire_condition -= random.uniform(0.1, 0.2)

    return race_result

def simulate_pitstop(team):
    # Simulate a pit stop based on driver skill and team performance
    pitstop_base = 0.5

    if team.pitcrew == "Terrible":
        pitstop = pitstop_base * random.uniform(0.875, 0.925)
        mistake_chance = 0.075
    elif team.pitcrew == "Poor":
        pitstop = pitstop_base * random.uniform(0.9, 0.95)
        mistake_chance = 0.06
    elif team.pitcrew == "Fair":
        pitstop = pitstop_base * random.uniform(0.925, 0.975)
        mistake_chance = 0.045
    elif team.pitcrew == "Great":
        pitstop = pitstop_base * random.uniform(0.95, 1.0)
        mistake_chance = 0.03
    elif team.pitcrew == "Excellent":
        pitstop = pitstop_base * random.uniform(0.975, 1.025)
        mistake_chance = 0.015
    
    if random.uniform(0, 1) < mistake_chance:
        # Simulate a pit stop mistake
        pitstop *= random.uniform(0.25, 0.5)

    return pitstop

def simulate_retirement(driver, team, starting_position, qualifying_results, iteration, iterations):
    num_drivers = len(qualifying_results)
    top_30 = int(num_drivers * 0.3)

    # Clamp team.reliability to be at most 0.99
    reliability = min(team.reliability, 0.99)
    threshold = 0.8

    race_wear = 1 - (iteration / iterations)

    if any(status in team.status for status in ['Start/Park']) and starting_position > top_30:
        reliability *= 0.1
        threshold *= 0.1

    if team.status != "Start/Park":
        if random.uniform(0, 1) > reliability:
            if random.uniform(0, 1) > race_wear:
                if random.uniform(0, 1) > threshold:
                    return "Retirement"
                else:
                    return ""
            else:
                return ""
        else:
            return ""
    else:
        if random.uniform(0, 1) > reliability:
            if random.uniform(0, 1) > threshold:
                return "Retirement"
            else:
                return ""
        else:
            return ""

def simulate_crash(driver, iterations):
    speed_vs_skill_difference = 1 + ((driver.skill - driver.speed) / 100)
    skill_vs_bravery_difference = 1 + ((driver.skill - driver.bravery) / 100)
    skill_probability = min((driver.skill * speed_vs_skill_difference * (skill_vs_bravery_difference)) / 100, 0.99)

    iteration_factor = 1 - (1 / iterations)

    # Compare random values with probabilities derived from driver skill and crash probability
    if random.uniform(0, 1) > skill_probability:
        if random.uniform(0, 1) > 0.925:
            if random.uniform(0, 1) > iteration_factor:
                return "Crash"
            else:
                return ""
        else:
            return ""
    else:
        return ""

def simulate_overtakes_blocks_clean_air(driver, team, teams, starting_position, new_race_results, iteration, iterations):
    race_result_mod = 0.0
    failure_collided_drivers = []
    num_drivers = len(new_race_results)

    # Overtake logic (can't happen in 1st place)
    if 1 < starting_position < num_drivers:
        # More frequent in the middle of the pack
        mid_factor = 1 - abs((starting_position - 1) - (num_drivers / 2)) / (num_drivers / 2)
        # Check cars ahead
        ahead_indices = [i for i in range(max(0, starting_position - 6), starting_position - 1)]
        # Weight for number of overtakes (favor fewer)
        overtake_weights = [0.5, 0.3, 0.15, 0.05, 0.025]
        if any(trait in driver.traits for trait in ['Aggressive']):
            overtake_weights = [0.45, 0.25, 0.15, 0.1, 0.075]
        if any(trait in driver.traits for trait in ['Cautious']):
            overtake_weights = [0.55, 0.35, 0.15, 0.025, 0.01]
        num_overtakes = random.choices(range(1, min(6, len(ahead_indices)+1)), weights=overtake_weights[:len(ahead_indices)], k=1)[0]
        overtakes_attempted = 0
        for idx in reversed(ahead_indices[-num_overtakes:]):
            other_team_name, other_driver_name, other_result = new_race_results[idx]
            perf_adv = (team.performance + team.power) - other_result
            bravery_factor = driver.bravery
            # Higher chance if performance advantage and bravery are high
            overtake_chance = 0.15 * mid_factor + 0.25 * max(0, perf_adv / 100) + 0.6 * (bravery_factor / 100)
            if any(trait in driver.traits for trait in ['GreatOvertaker']):
                overtake_chance *= 1.1
            if any(trait in driver.traits for trait in ['PoorOvertaker']):
                overtake_chance *= 0.9
            overtake_chance = min(overtake_chance, 0.85)
            # Success/failure
            skill_factor = 0.2 * (driver.skill / 100)
            speed_factor = 0.1 * (driver.speed / 100)
            success_chance = overtake_chance + skill_factor + speed_factor
            roll = random.uniform(0, 1)
            if roll < success_chance:
                race_result_mod += 0.025  # Successful overtake
            else:
                race_result_mod -= 0.01  # Failed overtake
                if random.uniform(0, 1) < 0.01:
                    # Critical failure: collision
                    # DEBUG print(f"Collision between {driver.name} and {other_driver_name} (overtake)")
                    if random.uniform(0, 1) < 0.75:
                        driver.dnf = "Collision"
                        failure_collided_drivers.append(driver.name)
                    if random.uniform(0, 1) < 0.5:
                        # Find the actual Driver object from the teams dictionary
                        for team in teams.values():
                            driver_obj = next((d for d in team.drivers if d.name == other_driver_name), None)
                            if driver_obj:
                                driver_obj.dnf = "Collision"
                                failure_collided_drivers.append(other_driver_name)
                                break
            overtakes_attempted += 1

    # Block logic (can't happen in last place)
    if 1 <= starting_position < num_drivers:
        # More frequent in the middle of the pack
        mid_factor = 1 - abs((starting_position - 1) - (num_drivers / 2)) / (num_drivers / 2)
        # Check cars behind
        behind_indices = [i for i in range(starting_position, min(num_drivers, starting_position + 5))]
        block_weights = [0.5, 0.3, 0.15, 0.05, 0.025]
        num_blocks = random.choices(range(1, min(6, len(behind_indices)+1)), weights=block_weights[:len(behind_indices)], k=1)[0]
        blocks_attempted = 0
        for idx in behind_indices[:num_blocks]:
            other_team_name, other_driver_name, other_result = new_race_results[idx]
            perf_disadv = other_result - (team.performance + team.power)
            skill_factor = driver.skill
            # Higher chance if performance disadvantage and skill are high
            block_chance = 0.15 * mid_factor + 0.25 * max(0, perf_disadv / 100) + 0.6 * (skill_factor / 100)
            if any(trait in driver.traits for trait in ['GreatBlocker']):
                block_chance *= 1.1
            if any(trait in driver.traits for trait in ['PoorBlocker']):
                block_chance *= 0.9
            block_chance = min(block_chance, 0.85)
            bravery_factor = 0.2 * (driver.bravery / 100)
            success_chance = block_chance + bravery_factor
            roll = random.uniform(0, 1)
            if roll < success_chance:
                race_result_mod += 0.0  # Successful block
            else:
                race_result_mod -= 0.025  # Failed block
                if random.uniform(0, 1) < 0.01:
                    # Critical failure: collision
                    # DEBUG print(f"Collision between {driver.name} and {other_driver_name} (block)")
                    if random.uniform(0, 1) < 0.75:
                        driver.dnf = "Collision"
                        failure_collided_drivers.append(driver.name)
                    if random.uniform(0, 1) < 0.5:
                        # Find the actual Driver object from the teams dictionary
                        for team in teams.values():
                            driver_obj = next((d for d in team.drivers if d.name == other_driver_name), None)
                            if driver_obj:
                                driver_obj.dnf = "Collision"
                                failure_collided_drivers.append(other_driver_name)
                                break
                    break
            blocks_attempted += 1

    # Clean air logic (fringes of race order, more as race spreads out)
    spread_factor = min(1.0, iteration / max(1, iterations))
    fringe_factor = max(0.0, (abs(starting_position - 1) / num_drivers) if starting_position == 1 else (abs(starting_position - num_drivers) / num_drivers))

    # Chance that clean air effect even happens at all
    activation_chance = 0.5 * spread_factor + 0.5 * fringe_factor
    if random.uniform(0, 1) < activation_chance:
        clean_air_chance = 0.5 * fringe_factor + 0.5 * spread_factor

        if any(trait in driver.traits for trait in ['GreatInCleanAir']):
            clean_air_chance *= 1.1
        if any(trait in driver.traits for trait in ['PoorInCleanAir']):
            clean_air_chance *= 0.9

        clean_air_chance = min(clean_air_chance, 0.95)

        speed_factor = 0.7 * (driver.speed / 100)
        skill_factor = 0.2 * (driver.skill / 100)

        success_chance = clean_air_chance + speed_factor + skill_factor
        roll = random.uniform(0, 1)

        if roll < success_chance:
            race_result_mod += 0.015  # Successful clean air
        else:
            race_result_mod -= 0.015  # Failed clean air

    return race_result_mod, failure_collided_drivers

def simulate_collision(new_race_results, teams, iterations):
    # List to store the drivers involved in collisions
    collided_drivers = []

    # Iterate over the sorted race results to check for proximity and collision chances
    for i, (team_name, driver_name, race_result) in enumerate(new_race_results):
        # Find the driver object corresponding to the driver_name
        team = next((team for team in teams.values() if team.name == team_name), None)
        driver = next((driver for driver in team.drivers if driver.name == driver_name), None) if team else None

        if not driver:
            continue  # Skip if the driver object is not found

        # Proximity threshold: Assume a driver is at risk of collision if they are within 3 positions
        proximity_candidates = []

        for j in range(i + 1, len(new_race_results)):
            if abs(i - j) <= 4:
                proximity_candidates.append(j)

        # Randomly select one or more `j` from the candidates, if any
        if proximity_candidates:
            num_collisions = min(4, len(proximity_candidates))
            weights = [0.5, 0.2, 0.1, 0.05][:num_collisions]
            selected_js = random.sample(proximity_candidates, k=random.choices(range(1, num_collisions + 1), weights=weights)[0])

            for selected_j in selected_js:
                other_team_name, other_driver_name, _ = new_race_results[selected_j]
                other_team = next((team for team in teams.values() if team.name == other_team_name), None)
                other_driver = next((driver for driver in other_team.drivers if driver.name == other_driver_name), None) if other_team else None

                if not other_driver:
                    continue  # Skip if the other driver object is not found

                # Simulate a collision chance
                speed_vs_skill_difference = 1 + ((driver.skill - driver.speed) / 100)
                skill_probability = min((driver.skill * speed_vs_skill_difference) / 100, 0.99)

                iteration_factor = 1 - (1 / iterations)

                # If a collision occurs (chance is met), mark both drivers as involved
                if random.uniform(0, 1) > min(driver.skill / 100, 0.999) and random.uniform(0, 1) > skill_probability:
                    if random.uniform(0, 1) > 0.99:
                        if random.uniform(0, 1) > iteration_factor:
                            if other_driver.dnf == "":  # Avoid marking the driver multiple times
                                driver.dnf = "Collision"
                                other_driver.dnf = "Collision"
                                collided_drivers.append(driver)
                                collided_drivers.append(other_driver)

    return collided_drivers


def calculate_fastest_lap_and_laps_led(sorted_qualifying_results, dnq_results, sorted_race_results, total_laps, base_time):
    fastest_lap_times = []
    qualifying_lap_times = []
    full_race_times = []
    formatted_race_times = []  # New list to store formatted race times for each driver
    formatted_qualifying_lap_times = []
    
    # Initialize laps_led dictionary
    laps_led = {driver: 0 for _, driver, _ in sorted_race_results}
    
    for i, ((team_name, driver_name), qualifying_result) in enumerate(sorted_qualifying_results):
        position = i + 1

        qualifying_result_factor = max(0, 0.05 * qualifying_result[1])  # Ensure non-negative contribution
        qualifying_lap_time = base_time - qualifying_result_factor
        qualifying_lap_times.append(qualifying_lap_time)

        # Format the quali time for display
        qualifying_lap_minutes = int(qualifying_lap_time // 60)
        qualifying_lap_seconds = qualifying_lap_time % 60
        formatted_time = "{:d}:{:05.2f}".format(qualifying_lap_minutes, qualifying_lap_seconds)

        formatted_qualifying_lap_times.append((driver_name, formatted_time))

    for i, ((team_name, driver_name), qualifying_result) in enumerate(dnq_results):
        position = i + 1

        qualifying_result_factor = max(0, 0.05 * qualifying_result[1])  # Ensure non-negative contribution
        qualifying_lap_time = base_time - qualifying_result_factor
        qualifying_lap_times.append(qualifying_lap_time)

        # Format the quali time for display
        qualifying_lap_minutes = int(qualifying_lap_time // 60)
        qualifying_lap_seconds = qualifying_lap_time % 60
        formatted_time = "{:d}:{:05.2f}".format(qualifying_lap_minutes, qualifying_lap_seconds)

        formatted_qualifying_lap_times.append((driver_name, formatted_time))

    for i, (team_name, driver_names, race_result) in enumerate(sorted_race_results):
        # Using the index as the finishing position
        position = i + 1

        # Simulate fastest lap time based on position and performance
        # Better positions should lead to better lap times (lower numbers)
        position_factor = (position - 1) / (len(sorted_race_results) - 1)  # Higher position, worse time
        race_result_factor = max(0, 0.05 * race_result)  # Ensure non-negative contribution
        fastest_lap_time = base_time + (position_factor * 5) - race_result_factor + random.uniform(0, 30)
        fastest_lap_times.append(fastest_lap_time)

        # Calculate full race time for this driver
        full_race_time = (base_time - race_result_factor) * total_laps
        full_race_times.append(full_race_time)  # Store each driver's race time
        
        # Format the full race time for display
        full_race_minutes = int(full_race_time // 60)
        full_race_seconds = full_race_time % 60
        formatted_race_times.append("{:d}:{:05.2f}".format(full_race_minutes, full_race_seconds))

        # Simulate laps led based on position and performance
        base_laps = 0
        for driver in driver_names.split(", "):  # Split in case there are multiple drivers
            # Calculate laps led but ensure it doesn’t exceed total_laps
            laps_led[driver] = max(0, int(base_laps + (1 - position_factor) * (total_laps / 4) + (race_result_factor / 10) - random.uniform(-15, 60)))
            # Clamp the laps led to not exceed total_laps
            laps_led[driver] = min(laps_led[driver], total_laps)

    # Find the fastest lap
    fastest_lap_index = fastest_lap_times.index(min(fastest_lap_times))
    fastest_lap_driver = sorted_race_results[fastest_lap_index][1]  # Getting the driver name
    fastest_lap_time = fastest_lap_times[fastest_lap_index]

    fastest_lap_minutes = int(fastest_lap_time // 60)
    fastest_lap_seconds = fastest_lap_time % 60
    fastest_lap_formatted = "{:d}:{:05.2f}".format(fastest_lap_minutes, fastest_lap_seconds)

    # Determine the driver with the most laps led
    most_laps_led_driver = max(laps_led, key=laps_led.get)
    most_laps_led_count = laps_led[most_laps_led_driver]

    return fastest_lap_driver, fastest_lap_formatted, most_laps_led_driver, most_laps_led_count, formatted_qualifying_lap_times, formatted_race_times

def extract_filename(filename):
    series_name = filename
    return series_name

def get_series_attributes_from_csv(series_name, directory):
    csv_file_path = os.path.join(directory, 'Championships', 'Rules', 'Championship Rules.csv')

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
                retirement_threshold = row['Retirement Threshold']  # Percentage of drivers that can retire
                return discipline, region, tier, team_rules, chassis_rules, engine_rules, practice_sessions, charter_system, charter_slots, retirement_threshold

    # If no match is found, raise an error
    raise ValueError(f"No match found for series_name: {series_name}")

def get_color_hex_from_csv(color_name, directory):
    csv_file_path = os.path.join(directory, 'Data', 'Colors.csv')
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"'Data Colors.csv' file not found in the specified directory: {csv_file_path}")
    
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Color'] == color_name:
                return row['Hex']
    
    raise ValueError(f"No match found for color_name: {color_name}")

def get_sponsor_branding_color_hex(sponsor_name, series_name, directory):
    csv_file_path = os.path.join(directory, 'World', 'Sponsors', f"Sponsors - {series_name}.csv")

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Sponsors file not found: {csv_file_path}")

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Name'] == sponsor_name:
                return row.get('Branding', '')

    raise ValueError(f"No match found for sponsor: {sponsor_name}")

def read_standings_data(series_name, script_directory, discipline):
    json_filepath = os.path.join(script_directory, 'Championships', 'Logs')

    most_recent_file = None
    most_recent_round = None

    # Initialize dictionaries to store standings data by category
    drivers_standings = []
    teams_standings = []
    entrants_standings = []

   # Iterate through each file in the directory
    for filename in os.listdir(json_filepath):
        # Check if the file is a standings file for the series
        if filename.endswith("Standings.json") and filename.startswith(series_name):
            parts = filename.split(" - ")
            try:
                round_number = int(parts[1].split()[1])  # Extract round number from "Round {number}"
                
                # If this is the first file or has a higher round, update the most recent file
                if most_recent_file is None or round_number > most_recent_round:
                    most_recent_round = round_number
                    most_recent_file = os.path.join(json_filepath, filename)
            except (IndexError, ValueError):
                print(f"Skipping file with unexpected format: {filename}")

    # Instead of raising an error, return None if no file was found
    if most_recent_file is None:
        return None  # Return None or any default value as needed

    # Load data from the most recent file
    with open(most_recent_file, 'r') as json_file:
        most_recent_standings = json.load(json_file)

    # Parse JSON data to populate each category
    for entry in most_recent_standings:
        # Check if it's a driver entry
        if "Rank" in entry:
            if discipline == "StockCar":
                drivers_standings.append({
                    "Rank": entry["Rank"],
                    "Driver": entry["Driver"],
                    "Team": entry["Team"],
                    "Points": entry["Points"],
                    "Wins": entry["Wins"],
                    "Top 5s": entry["Top 5s"],
                    "Top 10s": entry["Top 10s"],
                    "Poles": entry["Poles"],
                    "DNFs": entry["DNFs"],
                    "Races": entry["Races"]
                })
            else:
                drivers_standings.append({
                    "Rank": entry["Rank"],
                    "Driver": entry["Driver"],
                    "Team": entry["Team"],
                    "Points": entry["Points"],
                    "Wins": entry["Wins"],
                    "Podiums": entry["Podiums"],
                    "Poles": entry["Poles"],
                    "DNFs": entry["DNFs"],
                    "Races": entry["Races"]
                })
        
        # Check if it's a team entry
        elif "t_Rank" in entry:
            if discipline == "StockCar":
                teams_standings.append({
                    "Rank": entry["t_Rank"],
                    "Team": entry["t_Team"],
                    "Points": entry["t_Points"],
                    "Wins": entry["t_Wins"],
                    "Top 5s": entry["t_Top 5s"],
                    "Top 10s": entry["t_Top 10s"],
                    "Poles": entry["t_Poles"],
                    "DNFs": entry["t_DNFs"]
                })
            else:
                teams_standings.append({
                    "Rank": entry["t_Rank"],
                    "Team": entry["t_Team"],
                    "Points": entry["t_Points"],
                    "Wins": entry["t_Wins"],
                    "Podiums": entry["t_Podiums"],
                    "Poles": entry["t_Poles"],
                    "DNFs": entry["t_DNFs"]
                })

        # Check if it's an entrant entry
        elif "e_Rank" in entry:
            if discipline == "StockCar":
                entrants_standings.append({
                    "Rank": entry["e_Rank"],
                    "Entrant": entry["e_Entrant"],
                    "Points": entry["e_Points"],
                    "Wins": entry["e_Wins"],
                    "Top 5s": entry["e_Top 5s"],
                    "Top 10s": entry["e_Top 10s"],
                    "Poles": entry["e_Poles"],
                    "DNFs": entry["e_DNFs"],
                    "Races": entry["e_Races"]
                })
            else:
                entrants_standings.append({
                    "Rank": entry["e_Rank"],
                    "Entrant": entry["e_Entrant"],
                    "Points": entry["e_Points"],
                    "Wins": entry["e_Wins"],
                    "Podiums": entry["e_Podiums"],
                    "Poles": entry["e_Poles"],
                    "DNFs": entry["e_DNFs"],
                    "Races": entry["e_Races"]
                })

    # Return structured standings data
    return {
        "drivers_standings": drivers_standings,
        "teams_standings": teams_standings,
        "entrants_standings": entrants_standings
    }

def combine_driver_names(drivers):
    return " / ".join(driver.name for driver in drivers)

def main():
    # Get the directory path of the script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Get the filename without extension
    script_filename = os.path.splitext(os.path.basename(__file__))[0]

    # Assuming the series_name is derived directly from the script filename
    series_name = script_filename.split(" - ")[-1]  # Adjust this based on your filename format

    # Extract parts from the CSV file
    discipline, region, tier, team_rules, chassis_rules, engine_rules, practice_sessions, charter_system, charter_slots, retirement_threshold = get_series_attributes_from_csv(series_name, script_directory)

    # Construct the CSV file path
    csv_filename = f"{script_filename}.csv"
    csv_file_path = os.path.join(script_directory, csv_filename)

    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: {csv_filename} not found in the script directory.")
        return

    # Read data from CSV
    teams = {}
    drivers = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            team_name = row['Team']
            
            if team_name not in teams:
                teams[team_name] = Team(
                    team_name,
                    row['Charter'],
                    row['Alliance'],
                    row['Prestige'],
                    "",  # Initial color (will be updated later)
                    row['Status'],
                    row['Primary Sponsor'],     # Sponsor
                    row['Commitment'],  # Sponsor
                    row['Secondary Sponsors'],
                    row['Chassis'],
                    row['Design'],
                    row['Performance'],
                    row['Aero'],
                    row['Gearbox'],
                    row['Suspension'],
                    row['Brakes'],
                    row['Reliability'],
                    row['Characteristics'],
                    row['Engineer'],
                    row['Supplier'],
                    row['Engine'],
                    row['Power'],
                    row['Engine Reliability'],
                    row['Tires'],
                    row['Pit Crew'],
                    row['Strategist']
                )

            # Update color after ensuring team exists in the dictionary
            if teams[team_name].commitment.split("|")[0] == "Title":
                color_name = get_sponsor_branding_color_hex(
                    teams[team_name].primary_sponsor, series_name, script_directory
                )
            else:
                color_name = row['Color']

            # Handle multiple colors by randomly selecting one
            color_choices = color_name.split('|')
            selected_color_name = random.choice(color_choices).strip()

            # Replace with its hex value
            color_hex = get_color_hex_from_csv(selected_color_name, script_directory)

            # Update the team's color with the selected hex color
            teams[team_name].color = color_hex
            
            driver = Driver(
                row['Name'],
                row['Nationality'],
                row['Age'],
                row['Psyche'],
                row['Speed'],
                row['Skill'],
                row['Bravery'],
                row['Fitness'],
                row['Experience'],
                row['Morale'],
                row['Discipline'],
                row['Preference'],
                row['Style'],
                row['Traits'],
                row['Fame'],
                row['Reputation'],
                row['Funding'],
                row['Personal Sponsors'],
                row['Contract'],
                row['Target'],
                row['Relations'],
                team_name
            )
            
            teams[team_name].add_driver(driver)
            drivers.append(driver)

    # Construct the schedule CSV file path
    schedule_csv_path = os.path.join(script_directory, "Schedules", f"Schedule - {script_filename}.csv")

    # Check if the schedule CSV file exists
    if not os.path.exists(schedule_csv_path):
        print(f"Error: Schedule CSV file not found in the 'Schedules' subdirectory.")
        return

    # Read schedule data from CSV
    schedule = []
    with open(schedule_csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            schedule.append(row)

    # Sort schedule based on the "Order" column
    sorted_schedule = sorted(schedule, key=lambda x: int(x['Order']))

    # Check if the "Races" directory exists and get the most recent race file
    results_dir = os.path.join(script_directory, "Schedules", "Races")
    os.makedirs(results_dir, exist_ok=True)

    # Get all JSON files in the directory
    race_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]

    # Filter files for the same series
    series_race_files = [
        f for f in race_files if f.startswith(series_name)
    ]

    # Determine the most recent race order
    if series_race_files:
        # Extract the order from the filenames, assuming the format is "Series Name - Order - Circuit.json"
        race_orders = []
        for file in series_race_files:
            parts = file.split(" - ")
            if len(parts) >= 2:  # Ensure the filename has at least "Series Name - Order"
                try:
                    race_order = int(parts[1])  # Extract and convert the "Order" part to an integer
                    race_orders.append((race_order, file))
                except ValueError:
                    continue  # Skip files where the order isn't a valid integer

        # If race orders exist, find the highest order (most recent race)
        if race_orders:
            last_race_order, last_race_file = max(race_orders, key=lambda x: x[0])

            # Run the next race in the schedule
            next_race = next((race for race in sorted_schedule if int(race['Order']) > last_race_order), None)
            if next_race:
                race = next_race
            else:
                print(f"No remaining races to run in the schedule for {series_name}.")
                return
        else:
            # No valid race order was found, run the first race
            race = sorted_schedule[0]
    else:
        # No files exist for this series, run the first race in the schedule
        race = sorted_schedule[0]

    # At this point, 'race' contains the next race to run, either from the schedule or the first race

    # Extract race details (as before)
    order = race['Order']
    circuit = race['Circuit']
    country = race['Country']
    event = race['Event']
    circuit_type = race['Type']

    difficulty = float(race['Difficulty'])  # 0.0 to 1.0
    track_speed = race['Speed']             # Low / Medium / High

    clear_prob = float(race['Clear'])
    rainy_prob = float(race['Rainy'])
    overcast_prob = float(race['Overcast'])
    hot_prob = float(race['Hot'])
    stormy_prob = float(race['Stormy'])

    track_characteristics = race['Characteristics'].split('|')

    total_laps = float(race['Laps'])
    base_time = float(race['Base Time'])
    lap_record = race['Lap Record']
    grid_size = int(race['Grid Size'])

    # Simulate weather for the event
    weather_condition = simulate_weather(clear_prob, rainy_prob, overcast_prob, hot_prob, stormy_prob)

    print(f"\n(Round {order}: {circuit} - {country} - {circuit_type} - {int(total_laps)} laps)\n")
    print(f"Weather: {weather_condition}")
    print(f"Lap Record: {lap_record}")

    # Wait for user input before displaying qualifying results
    # input("\n...")

    time.sleep(0.75)  # Add a delay between each entry

    # Qualifying
    qualifying_results = {}
    for team in teams.values():
        for driver in team.drivers:
            result = simulate_qualifying(team, weather_condition, discipline, event, grid_size, circuit_type, series_name, script_directory, track_speed, track_characteristics, sorted_schedule, race, practice_sessions, difficulty)
            
            if result is not None:  # Skip if qualifying result is None
                qualified_drivers, dnq_drivers = result  # Extract qualified and DNQ lists

                # Store qualifying times for individual drivers
                for qualifying_time in qualified_drivers:
                    qualifying_results[(team.name, driver.name)] = (driver, qualifying_time)  # Qualified drivers
                                                            # JACKPOT! ^

    # Sort qualifying results and DNQ results separately based on the times
    sorted_qualifying_results = sorted(qualifying_results.items(), key=lambda x: x[1][1], reverse=True)

    # Apply grid size limit
    dnq_results = sorted_qualifying_results[grid_size:]
    sorted_qualifying_results = sorted_qualifying_results[:grid_size]

    # Ensure drivers with empty team.charter are in sorted_qualifying_results
    for driver in dnq_results[:]:
        team_name, driver_name = driver[0]
        team = teams[team_name]
        if team.charter == "TRUE":
            # Move driver to sorted_qualifying_results
            sorted_qualifying_results.append(driver)
            dnq_results.remove(driver)

    # Ensure grid size limit is maintained
    while len(sorted_qualifying_results) > grid_size:
        # Move the lowest driver to dnq_results, but ensure drivers with empty team.charter are not moved
        for i in range(len(sorted_qualifying_results) - 1, -1, -1):
            team_name, driver_name = sorted_qualifying_results[i][0]
            team = teams[team_name]
            if team.charter != "TRUE":
                dnq_results.append(sorted_qualifying_results.pop(i))
                break

    # Sort the DNQ results by time
    dnq_results = sorted(dnq_results, key=lambda x: x[1][1], reverse=True)

    # Race
    race_results = []
    position_changes = []
    iteration = 0  # Initialize iteration before using it
    iterations = int((total_laps * base_time) / 750)  # Initialize iterations before using it
    for i, ((team_name, driver_name), _) in enumerate(sorted_qualifying_results):
        team = teams[team_name]
        starting_position = i + 1
        if team.drivers:  # Check if the team has at least one driver
            race_result = simulate_race(team.drivers[0], team, starting_position, weather_condition, discipline, circuit_type, qualifying_results, sorted_qualifying_results, track_characteristics, iteration, iterations)
            race_results.append((team_name, driver_name, race_result))
        else:
            pass  # Do nothing if no drivers available for the team

    # Sort race results by performance score after the race
    sorted_race_results = sorted(race_results, key=lambda x: (x[2] != 0, x[2]), reverse=True)

    # Simulate the race over multiple iterations
    for iteration in range(iterations):
        new_race_results = []
        for i, (team_name, driver_name, _) in enumerate(sorted_race_results):
            team = teams[team_name]
            starting_position = i + 1
            if team.drivers:  # Check if the team has at least one driver
                driver = team.drivers[0]
                if driver.dnf == "Retirement" or driver.dnf == "Crash" or driver.dnf == "Collision":
                    race_result = 0  # Mark the race result as 0 for retirement
                else:
                    race_result = simulate_race(driver, team, starting_position, weather_condition, discipline, circuit_type, qualifying_results, sorted_race_results, track_characteristics, iteration, iterations)
                new_race_results.append((team_name, driver_name, race_result))
            else:
                pass  # Do nothing if no drivers available for the team

        # Apply overtakes/blocks/clean air effects for each driver in new_race_results
        for i, (team_name, driver_name, race_result) in enumerate(new_race_results):
            team = teams[team_name]
            driver = next((d for d in team.drivers if d.name == driver_name), None)
            if driver:
                race_result_mod, failure_collided_drivers = simulate_overtakes_blocks_clean_air(
                    driver, team, teams, i + 1, new_race_results, iteration, iterations)
                # Set race result to 0 for collided drivers
                if failure_collided_drivers:
                    new_race_results[i] = (team_name, driver_name, 0)
                    for collided_name in failure_collided_drivers:
                        for j, (tname, dname, rresult) in enumerate(new_race_results):
                            if dname == collided_name:
                                new_race_results[j] = (tname, dname, 0)
                else:
                    # Apply race_result_mod if not DNF
                    if race_result != 0:
                        new_race_results[i] = (team_name, driver_name, race_result + (race_result * race_result_mod))

        # Simulate collisions after each iteration
        collided_drivers = simulate_collision(new_race_results, teams, iterations)
        for collided_driver in collided_drivers:
            for i, (team_name, driver_name, race_result) in enumerate(new_race_results):
                if collided_driver.name == driver_name:
                    new_race_results[i] = (team_name, driver_name, 0)  # Set race result to 0 for collided drivers
                    break

        # Sort race results by performance score after each iteration
        sorted_race_results = sorted(new_race_results, key=lambda x: (x[2] != 0, x[2]), reverse=True)

        # # Print the winner of each iteration except the last one
        # DEBUG if iteration < iterations - 1:
        #     print(f"Iteration {iteration + 1} Results:")
        #     for pos, (team_name, driver_name, race_result) in enumerate(sorted_race_results):
        #         driver = next((d for d in teams[team_name].drivers if d.name == driver_name), None)
        #         if driver:
        #             # Find the previous position of the driver
        #             previous_position = next(
        #             (prev_pos for prev_pos, (prev_team_name, prev_driver_name, _) in enumerate(new_race_results)
        #             if prev_team_name == team_name and prev_driver_name == driver_name),
        #             None
        #             )
        #             # Calculate movement
        #             movement = previous_position - pos if previous_position is not None else None
        #             movement_str = f"({movement:+})" if movement is not None else "(N/A)"
        #             print(f"{pos + 1}. {driver_name} ({team_name}) with score {race_result} {movement_str}")
        #     print("\n")

    # Calculate position changes by comparing original qualifying position with final race position
    for race_position, (team_name_race, driver_name_race, race_result) in enumerate(sorted_race_results):
        for qual_position, ((team_name_qual, driver_name_qual), _) in enumerate(sorted_qualifying_results):
            if team_name_race == team_name_qual and driver_name_race == driver_name_qual:
                # Calculate position change
                position_change = qual_position - race_position
                position_changes.append((team_name_race, driver_name_race, position_change))
                break  # Stop inner loop once we find the match

    highest_position_change = max(position_changes, key=lambda x: x[2])

    # Extract relevant information
    highest_team_name, highest_driver_name, position_change = highest_position_change

    console = Console()

    fastest_lap_driver, fastest_lap_time, most_laps_led_driver, most_laps_led_count, formatted_qualifying_lap_times, formatted_race_times = calculate_fastest_lap_and_laps_led(sorted_qualifying_results, dnq_results, sorted_race_results, total_laps, base_time)

    # Shuffle entries randomly
    randomized_results = sorted_qualifying_results.copy()
    random.shuffle(randomized_results)

    # List to keep track of entries that have been "revealed"
    revealed_results = []

    # Function to build the current leaderboard as Text
    def build_leaderboard_text(revealed_results, new_entry=None):
        leaderboard_text = Text("\n - - - Qualifying Order - - - \n\n")
        
        if not revealed_results:
            return leaderboard_text
        
        # Calculate max lengths for alignment
        max_name_length = max(len(driver_name) for (_, driver_name), _ in revealed_results)
        max_order_length = len(str(len(revealed_results)))

        # Build each line for the leaderboard
        for i, ((team_name, driver_name), qualifying_result) in enumerate(revealed_results):
            supplier = teams[team_name].supplier

            color = teams[team_name].color

            main_team_name, *rest = team_name.split("- ")

            if teams[team_name].alliance != "":
                rest.append(f"/ {teams[team_name].alliance}")

            colored_team_name = Text(main_team_name, style=color)

            # Find the correct formatted qualifying lap time for this driver from qualifying_data
            driver_qualifying_time = next(time for name, time in formatted_qualifying_lap_times if name == driver_name)

            # Construct the line for each driver
            line = Text(f"{i+1:2}. {driver_name.ljust(max_name_length)}     ({driver_qualifying_time})     (")
            line.append(colored_team_name)
            if rest:
                line.append(f" - {' '.join(rest)}")
            if supplier:
                line.append(f" - {supplier}")
            line.append(")\n")

            # Make the new entry bold
            if new_entry and (team_name, driver_name) == new_entry:
                line.stylize("bold")

            leaderboard_text.append(line)

        return leaderboard_text

    # Use Live to update the leaderboard in place
    with Live(build_leaderboard_text(revealed_results), refresh_per_second=4, console=console) as live:
        for team_driver, qualifying_result in randomized_results:
            # Add the new result to the revealed list and sort it
            revealed_results.append((team_driver, qualifying_result))
            revealed_results.sort(key=lambda x: x[1][1], reverse=True)  # Sort by qualifying result (time or score)

            # Update the leaderboard display with the new entry highlighted
            live.update(build_leaderboard_text(revealed_results, new_entry=team_driver))
            time.sleep(0.5)  # Delay to simulate qualifying results coming in progressively

   # Print DNQ drivers
    if dnq_results:
        print("\n - - - Failed to Qualify - - - \n")
        for i, ((team_name, driver_name), qualifying_result) in enumerate(dnq_results):
            supplier = teams[team_name].supplier

            color = teams[team_name].color

            main_team_name, *rest = team_name.split("- ")

            if teams[team_name].alliance != "":
                rest.append(f"/ {teams[team_name].alliance}")

            colored_team_name = Text(main_team_name, style=color)

            max_name_length = max(len(driver_name) for (_, driver_name), _ in sorted_qualifying_results)

            # Find the correct formatted qualifying lap time for this driver from qualifying_data
            driver_qualifying_time = next(time for name, time in formatted_qualifying_lap_times if name == driver_name)

            # Construct the full line with colors
            line = Text(f"{i+1+grid_size:2}. {driver_name.ljust(max_name_length)}     ({driver_qualifying_time})     (")
            line.append(colored_team_name)  # Add the colored team name
            if rest:
                line.append(f" - {' '.join(rest)}")  # Append remaining team name, if exists
            if supplier:
                line.append(f" - {supplier}")
            line.append(")")

            console.print(line)
            time.sleep(0.25)  # Add a delay between each entry

    time.sleep(1)  # Add a delay between each entry

    # Initialize MarkovChain
    markov = MarkovChain()
    markov.load_from_csv(script_directory, delimiter='|')

    def insert_curses(text):
        # Smaller numbers of curse insertions are weighted higher
        weights = [0.75, 0.5, 0.05, 0.025, 0.025]
        num_curses = random.choices(range(0, 5), weights=weights, k=1)[0]
        for _ in range(num_curses):
            words = text.split()
            if len(words) > 2:
                idx = random.randint(1, len(words) - 2)
                words.insert(idx, random.choice(["d*** well", "f******", "f******", "freaking", "honestly", "seriously", "effing", "bloody", "absolutely"]))
                text = " ".join(words)
        return text

    print("\n\n - - - Post-Qualifying News - - - \n")

    for i, ((team_name, driver_name), (driver, qualifying_result)) in enumerate(sorted_qualifying_results):
        num_drivers = len(sorted_qualifying_results)
        top_25 = int(num_drivers * 0.25)
        bottom_25 = int(num_drivers * 0.75)

        if i <= top_25 and i <= driver.target:
            if random.uniform(0, 1) < 0.4 or i == 0:  # Allow more interviews for top drivers
                text = markov.generate("Good Interview", driver_name=driver_name, team_name=team_name)
                text = insert_curses(text)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")

        if i >= bottom_25 and i >= driver.target:
            if random.uniform(0, 1) < 0.2:
                text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
                text = insert_curses(text)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")
    
    for i, ((team_name, driver_name), qualifying_result) in enumerate(dnq_results):
        if random.uniform(0, 1) < 0.2:
            text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
            text = insert_curses(text)
            print(f"INTERVIEW - ({driver_name} - DNQ):       '" + text + "'")

    # keyboard.wait('space')
    time.sleep(1.5)  # Add delay between each entry

    # Print race results with team name
    print("\n\n\n - - - Race Results - - - \n")
    max_name_length_race = max(len(driver_name) for _, driver_name, _ in sorted_race_results)
    max_order_length_race = len(str(len(sorted_race_results)))  # Length of the highest numbered order

    # Separate finished drivers from DNF drivers
    finished_drivers = []
    dnf_drivers = []

    for i, (team_name, driver_name, race_result) in enumerate(sorted_race_results):
        supplier = teams[team_name].supplier

        color = teams[team_name].color

        main_team_name, *rest = team_name.split("- ")

        if teams[team_name].alliance != "":
            rest.append(f"/ {teams[team_name].alliance}")

        colored_team_name = Text(main_team_name, style=color)

        driver = next((driver for driver in teams[team_name].drivers if driver.name in driver_name.split(' / ')), None)  # Find correct driver object
        if race_result == 0 and driver and (driver.dnf == "Crash" or driver.dnf == "Collision" or driver.dnf == "Retirement"):
            dnf_drivers.append((team_name, driver_name, driver.dnf, supplier, color))
        else:
            finished_drivers.append((team_name, driver_name, race_result, supplier, color))

    # Print finished drivers
    for i, (team_name, driver_name, race_result, supplier, color) in enumerate(finished_drivers):
        main_team_name, *rest = team_name.split("- ")  # Split team name

        if teams[team_name].alliance != "":
            rest.append(f"/ {teams[team_name].alliance}")
    
        color = teams[team_name].color

        colored_team_name = Text(main_team_name, style=color)

        # Construct the output line
        line = Text(f"{i+1:>{max_order_length_race}}. {driver_name.ljust(max_name_length_race)}     ({formatted_race_times[i]})     (")
        line.append(colored_team_name)  # Add colored team name
        if rest:
            line.append(f" - {' '.join(rest)}")
        if supplier:
            line.append(f" - {supplier}")
            # DEBUG line.append(f" - {supplier} ({race_result})")
        line.append(")")

        console.print(line)
        time.sleep(0.5)  # Add delay between each entry

    # Print DNF drivers
    for team_name, driver_name, dnf_reason, supplier, color in dnf_drivers:
        main_team_name, *rest = team_name.split("- ")  # Split team name

        if teams[team_name].alliance != "":
            rest.append(f"/ {teams[team_name].alliance}")

        color = teams[team_name].color

        colored_team_name = Text(main_team_name, style=color)

        # Construct the output line for DNF
        line = Text(f"{'(DNF)':<5} {driver_name.ljust(max_name_length_race)}     (")
        line.append(colored_team_name)  # Add colored team name
        if rest:
            line.append(f" - {' '.join(rest)}")
        if supplier:
            line.append(f" - {supplier}")
        line.append(")          -- ")
        line.append(Text(dnf_reason, style="italic"))  # Style DNF reason in bold red for emphasis

        console.print(line)
        time.sleep(0.25)  # Add delay between each entry

    print(f"\nFastest Lap: {fastest_lap_driver} - {fastest_lap_time}")
    print(f"Most Laps Led: {most_laps_led_driver} - {most_laps_led_count} laps led")
    print(f"Most Positions Gained: {highest_driver_name} - +{position_change} positions gained")

    time.sleep(1)

    # Post-Race News
    print("\n\n - - - Post-Race News - - - \n")
    
    for i, (team_name, driver_name, race_result) in enumerate(sorted_race_results):
        num_drivers = len(sorted_race_results)
        top_20 = int(num_drivers * 0.2)
        bottom_20 = int(num_drivers * 0.8)

        if i == 0:
            if random.uniform(0, 1) < 0.5:
                print(f"{driver_name} ({team_name}) takes victory!\n")
            else:
                print(f"{driver_name} ({team_name}) wins!\n")
        if i == 0:
            second_place = sorted_race_results[1][1]
            second_place_team = sorted_race_results[1][0]
            if random.uniform(0, 1) < 0.5:  # Adjust the probability as needed
                if random.uniform(0, 1) < 0.5:
                    print(f"{driver_name} ({team_name}) beats {second_place} ({second_place_team}) to take victory!\n")
                else:
                    print(f"{driver_name} ({team_name}) outduels {second_place} ({second_place_team}) for the win!\n")

    for i, (team_name, driver_name, race_result, _, _) in enumerate(finished_drivers):
        num_drivers = len(finished_drivers)
        top_25 = int(num_drivers * 0.25)
        bottom_25 = int(num_drivers * 0.75)
        if i <= top_25 and i <= driver.target:
            if random.uniform(0, 1) < 0.5 or i == 0:  # Adjust the probability as needed
                text = markov.generate("Good Interview", driver_name=driver_name, team_name=team_name)
                text = insert_curses(text)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")

        if i >= bottom_25 and i >= driver.target:
            if random.uniform(0, 1) < 0.25:  # Adjust the probability as needed
                text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
                text = insert_curses(text)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")
    
    for i, (team_name, driver_name, _, _, _) in enumerate(dnf_drivers):
        if random.uniform(0, 1) < 0.25:  # Adjust the probability as needed
            text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
            text = insert_curses(text)
            print(f"INTERVIEW - ({driver_name} - DNF):       '" + text + "'")

    # Save race results to a JSON file
    race_results_data = {
        "Series": series_name,
        "Order": order,
        "Circuit": circuit,
        "Event": event,
        "Weather": weather_condition,
        "Lap Record": lap_record,
        "Qualifying Results": [
            {"Position": i + 1, "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].primary_sponsor, "Time": formatted_qualifying_lap_times[i][1]}
            for i, ((team_name, driver_name), qualifying_result) in enumerate(sorted_qualifying_results)
        ],
        "DNQ Drivers": [
            {"Position": i + 1 + grid_size, "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].primary_sponsor, "Time": next(time for name, time in formatted_qualifying_lap_times if name == driver_name)}
            for i, ((team_name, driver_name), qualifying_result) in enumerate(dnq_results)
        ],
        "Race Results": [
            {"Position": i + 1, "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].primary_sponsor, "Time": formatted_race_times[i]}
            for i, (team_name, driver_name, race_result, _, _) in enumerate(finished_drivers)
        ],
        "DNF Drivers": [
            {"Position": "DNF", "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].primary_sponsor, "Reason": dnf_reason}
            for team_name, driver_name, dnf_reason, _, _ in dnf_drivers
        ],
        "Fastest Lap": {"Driver": fastest_lap_driver, "Time": fastest_lap_time},
        "Most Laps Led": {"Driver": most_laps_led_driver, "Laps": most_laps_led_count}
    }

    # Create the directory if it doesn't exist
    results_dir = os.path.join(script_directory, "Schedules", "Races")
    os.makedirs(results_dir, exist_ok=True)

    # Construct the JSON filename
    json_filename = f"{series_name} - {order} - {circuit}.json"
    json_file_path = os.path.join(results_dir, json_filename)

    # Write the race results to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(race_results_data, json_file, indent=4)

if __name__ == "__main__":
    main()