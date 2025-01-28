import csv
import random
import os
import time
import json
from collections import defaultdict
from rich.console import Console
from rich.text import Text
from rich.live import Live

class Driver:
    def __init__(self, name, nationality, age, speed, skill, experience, morale, preferred_discipline, preference, traits, fame, reputation, partner, contract, target, relations, team_name):
        self.name = name
        self.nationality = nationality
        self.age = float(age)
        self.speed = float(speed)
        self.skill = float(skill)
        self.experience = float(experience)
        self.morale = float(morale)
        self.preferred_discipline = preferred_discipline
        self.preference = preference
        self.traits = traits.split("|")  # Split traits by "|"
        self.fame = float(fame)
        self.reputation = float(reputation)
        self.partner = partner
        self.contract = contract
        self.target = target
        self.relations = relations

        self.team_name = team_name
        self.dnf = ""
        self.fantastic_qualifying = False
        self.fantastic_race = False
        self.shocking_qualifying = False
        self.shocking_race = False

class Team:
    def __init__(self, name, charter, alliance, prestige, color, status, sponsor, branding, commitment, chassis, performance, aero, gearbox, suspension, brakes, reliability, characteristics, wear, supplier, power, tires, strategist):
        self.name = name
        self.charter = charter
        self.alliance = alliance
        self.prestige = prestige
        self.color = color
        self.status = status.split("|")  # Split traits by "|"
        self.sponsor = sponsor
        self.branding = branding
        self.commitment = commitment        # Format: "Type/Duration/TypeOfDuration" (Type - Title/Primary/Secondary/Premier)
        self.chassis = chassis
        self.performance = float(performance)
        self.aero = float(aero)
        self.gearbox = float(gearbox)
        self.suspension = float(suspension)
        self.brakes = float(brakes)
        self.reliability = float(reliability)
        self.characteristics = characteristics.split("|")  # Split traits by "|"
        self.wear = float(wear)
        self.supplier = supplier
        self.power = float(power)
        self.tires = tires
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
        if sentence[-1] not in ".!…?":
            return sentence + random.choice(".....!!……?")
        if sentence[-1] in ",;":
            return sentence + random.choice(".....!!……?")
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
        team.performance *= 0.7
        team.power *= 0.7

        if all(trait not in driver.traits for trait in ['WetWeatherSpecialist']):
            driver.speed *= 0.9
            driver.skill *= 0.9

def circuit_type_modifier(circuit_type, driver, team):

    if circuit_type == 'Grand Prix':
        if driver.preference not in ['Road', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

    if circuit_type == 'Road Course':
        if driver.preference not in ['Road', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

    if circuit_type == 'Street Track':
        if driver.preference not in ['Road', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['StreetTrackSpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1
        
        if any(characteristic in team.characteristics for characteristic in ['StreetTrackSpecialist']):
            team.performance *= 1.1
            team.power *= 1.1

    if circuit_type == 'Short Track':
        if driver.preference not in ['Oval', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

        if any(trait in driver.traits for trait in ['ShortTrackSpecialist']):
            driver.speed *= 1.1
            driver.skill *= 1.1

        if any(characteristic in team.characteristics for characteristic in ['ShortTrackSpecialist']):
            team.performance *= 1.1
            team.power *= 1.1
    
    if circuit_type == 'Oval':
        if driver.preference not in ['Oval', 'Both']:
            driver.speed *= 0.85
            driver.skill *= 0.85

    if circuit_type == 'Superspeedway':
        if driver.preference not in ['Oval', 'Both']:
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

def experience_modifier(driver):
    driver.speed *= 1 - (1 - driver.experience) / 2
    driver.skill *= 1 - (1 - driver.experience) / 2

def trait_modifier(driver):
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

    # if any(trait in driver.traits for trait in ['Rattled']):
    #     random_value = random.uniform(0, 1)
    #     if random_value < 0.5:
    #         driver.speed *= random.uniform(0.8, 0.9) # Slower due to hesitation
    #     elif random_value > 0.75:
    #         driver.skill *= random.uniform(0.8, 0.9) # Decreased skill under pressure
    #     else:
    #         pass
    
    # if any(trait in driver.traits for trait in ['Sick']):
    #     driver.speed *= random.uniform(0.85, 0.95)
    #     driver.skill *= random.uniform(0.85, 0.95)

def race_trait_modifier(driver, starting_position, qualifying_results, track_characteristics):
    num_drivers = len(qualifying_results)
    bottom_25 = int(num_drivers * 0.75)

    if starting_position > bottom_25:
        if any(trait in driver.traits for trait in ['Heroic']):
            driver.speed *= 1.05
            driver.skill *= 1.05
        if any(trait in driver.traits for trait in ['Passive']):
            driver.speed *= 0.9
            driver.skill *= 0.9
    
    if starting_position == 0:
        if any(trait in driver.traits for trait in ['PoorFromPole']):
            driver.speed *= 0.9
            driver.skill *= 0.9
        if any(trait in driver.traits for trait in ['GreatFromPole']):
            driver.speed *= 1.05
            driver.skill *= 1.05
    
    if any(trait in driver.traits for trait in ['GoodInstincts']):
        random_value = random.uniform(0, 1)
        if random_value < 0.5:
            driver.skill *= random.uniform(1.025, 1.075)
    
    if any(t_characteristic in track_characteristics for t_characteristic in ['Prestigous']):
        random_value = random.uniform(0, 1)
        if random_value < 0.15:
            driver.skill *= random.uniform(0.95, 0.975)

def calculate_team_average_attributes(team, discipline):
    total_speed, total_skill, num_drivers = 0, 0, len(team.drivers)
    for driver in team.drivers:
        total_speed += driver.speed
        total_skill += driver.skill

    team.average_speed = total_speed / num_drivers if num_drivers > 0 else 0
    team.average_skill = total_skill / num_drivers if num_drivers > 0 else 0

    if discipline != 'Endurance':
        # Discipline-specific adjustments can go here
        pass

def simulate_practice(driver, team, track_speed, track_characteristics):
    def apply_modifier(attribute, base_multiplier, wear):
        if random.uniform(0, 1) > ((attribute / 100) * (1 - wear)):
            team.performance *= base_multiplier
            if random.uniform(0, 1) > ((attribute / 100) * (1 - wear)):
                opposite_attribute = 100 - attribute  # Convert attribute to its opposite on a scale from 0-100
                team.performance *= (base_multiplier - (opposite_attribute / 500))  # Adjust multiplier based on opposite attribute value

    if any(t_characteristic in track_characteristics for t_characteristic in ['Windy']):
        team.aero *= 0.9
    
    if any(t_characteristic in track_characteristics for t_characteristic in ['PoorTrackSurface']):
        team.suspension *= 0.9

    if track_speed == 'Low':
        team.brakes *= 0.95
        apply_modifier(team.aero, 0.975, team.wear)
        apply_modifier(team.gearbox, 0.95, team.wear)
        apply_modifier(team.suspension, 0.95, team.wear)
        apply_modifier(team.brakes, 0.925, team.wear)

        team.power *= 0.75

    if track_speed == 'Medium':
        apply_modifier(team.aero, 0.95, team.wear)
        apply_modifier(team.gearbox, 0.95, team.wear)
        apply_modifier(team.suspension, 0.95, team.wear)
        apply_modifier(team.brakes, 0.95, team.wear)

    if track_speed == 'High':
        team.aero *= 0.95
        apply_modifier(team.aero, 0.925, team.wear)
        apply_modifier(team.gearbox, 0.95, team.wear)
        apply_modifier(team.suspension, 0.95, team.wear)
        apply_modifier(team.brakes, 0.975, team.wear)

        team.power *= 1.25

def simulate_qualifying(team, weather_condition, discipline, event, grid_size, circuit_type, series_name, script_directory, track_speed, track_characteristics):
    standings_data = read_standings_data(series_name, script_directory, discipline)

    # List to store qualifying results for all drivers in the team
    qualifying_results = []

    # Create a copy of the drivers list to iterate over
    drivers_copy = team.drivers[:]

    for driver in drivers_copy:
        # Apply modifiers. Effects are applied to the race def as well
        weather_modifier(weather_condition, driver, team)
        circuit_type_modifier(circuit_type, driver, team)
        discipline_modifier(discipline, driver)
        experience_modifier(driver)
        trait_modifier(driver)

        simulate_practice(driver, team, track_speed, track_characteristics)

        # Check and remove drivers based on contract status and probabilities
        if any(status in team.status for status in ['Insecure']) and event != 'Premier'and random.uniform(0, 1) < 0.1:
            team.drivers.remove(driver)
            continue

        if any(status in team.status for status in ['Limited']) and event != 'Premier' and random.uniform(0, 1) < 0.66:
            team.drivers.remove(driver)
            continue

        if any(status in team.status for status in ['Guest']) and random.uniform(0, 1) < 0.95:
            team.drivers.remove(driver)
            continue

        # For Premier contract, ensure they participate in "Premier" events
        if any(status in team.status for status in ['Premier']) and event != 'Premier' and random.uniform(0, 1) < 0.95:
            continue

        driver.fantastic_qualifying = False  # Reset fantastic_qualifying attribute
        driver.shocking_qualifying = False  # Reset shocking_qualifying attribute
        driver.fantastic_race = False
        driver.shocking_race = False

        randomness = random.uniform(-24, 24)
        fantastic_chance = 0.005
        shocking_chance = 0.0075

        fantastic_chance += (driver.speed / 10000)
        shocking_chance += ((100 - driver.speed) / 10000)

        if team.strategist == "Terrible":
            fantastic_chance *= random.uniform(0.875, 0.925)
            shocking_chance *= random.uniform(1.075, 1.125)
        elif team.strategist == "Poor":
            fantastic_chance *= random.uniform(0.925, 0.975)
            shocking_chance *= random.uniform(1.025, 1.075)
        # elif team.strategist == "Fair":
        #     fantastic_chance *= random.uniform(1)
        #     shocking_chance *= random.uniform(1)
        elif team.strategist == "Great":
            fantastic_chance *= random.uniform(1.025, 1.075)
            shocking_chance *= random.uniform(0.925, 0.975)
        elif team.strategist == "Excellent":
            fantastic_chance *= random.uniform(1.075, 1.125)
            shocking_chance *= random.uniform(0.875, 0.925)

        if weather_condition == 'Clear':
            randomness = random.uniform(-24, 24)
            if random.uniform(0, 1) < fantastic_chance:
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < shocking_chance:
                driver.shocking_qualifying = True

        elif weather_condition == 'Rainy':
            randomness = random.uniform(-36, 36)
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
            randomness = random.uniform(-48, 48)
            if random.uniform(0, 1) < (fantastic_chance * 5):
                driver.fantastic_qualifying = True
            if random.uniform(0, 1) < (shocking_chance * 5):
                driver.shocking_qualifying = True
        
        # Store the original skill value
        original_skill = driver.skill
        original_speed = driver.speed

        special_modifier = 1
        if driver.fantastic_qualifying:
            print(f"{driver.name} Fantastic Qualifying")
            if random.uniform(0, 1) < 0.75:
                special_modifier *= 1.15
                if random.uniform(0, 1) < 0.5:
                    print(f"{driver.name} Even More Fantastic (Q)")
                    special_modifier *= 1.1
                    if random.uniform(0, 1) < 0.25:
                        print(f"{driver.name} EVEN MORE FANTASTIC")
                        special_modifier *= 1.05
            else:
                special_modifier *= 1.15

        if driver.shocking_qualifying:
            print(f"{driver.name} Shocking Qualifying")
            if random.uniform(0, 1) < 0.75:
                special_modifier *= 0.85
                if random.uniform(0, 1) < 0.5:
                    print(f"{driver.name} Even More Shocking (Q)")
                    special_modifier *= 0.9
                    if random.uniform(0, 1) < 0.25:
                        print(f"{driver.name} EVEN MORE SHOCKING")
                        special_modifier *= 0.95
            else:
                special_modifier *= 0.85

        # Calculate randomness based on starting position
        if circuit_type in ['Superspeedway']:
            randomness *= 1.6
        elif circuit_type in ['Oval']:
            randomness *= 1.4
        elif circuit_type in ['Short Track']:
            randomness *= 1.25

        if discipline == 'StockCar':
            randomness *= 1.15

        qualifying_result = (((driver.speed + (driver.skill / 2)) * 0.75) * special_modifier) + (team.performance * (1 - (0.75 * team.wear))) + team.power + randomness
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

def simulate_race(driver, team, starting_position, weather_condition, discipline, circuit_type, qualifying_results, sorted_qualifying_results, track_characteristics):
    # Reset qualifying attributes for the race simulation
    driver.fantastic_qualifying = False  # Reset fantastic_qualifying attribute
    driver.shocking_qualifying = False  # Reset shocking_qualifying attribute

    race_trait_modifier(driver, starting_position, qualifying_results, track_characteristics)

    if not team.drivers:
        # If there are no drivers in the team, return a performance score of 0
        return 0

    collided_drivers = []
    if driver.dnf != "Collision":
        # Assuming sorted_qualifying_results is already sorted by qualifying position
        collided_drivers = simulate_collision(sorted_qualifying_results)
    
    if collided_drivers:
        # If there is a collision, mark all affected drivers as DNF
        for collided_driver in collided_drivers:
            collided_driver.dnf = "Collision"
            # Return a performance score of 0 for these drivers
            if collided_driver == driver:
                return 0

    if simulate_crash(driver) == "Crash":
        driver.dnf = "Crash"
        # If the driver crashes, return a performance score of 0
        return 0

    if simulate_retirement(driver, team, starting_position, qualifying_results) == "Retirement":
        driver.dnf = "Retirement"
        # If the driver encounters a mechanical issue, return a performance score of 0
        return 0

    # Store the original skill value
    original_skill = driver.skill
    original_speed = driver.speed

    randomness = random.uniform(-24, 24)
    fantastic_chance = 0.0035
    shocking_chance = 0.015

    if any(t_characteristic in track_characteristics for t_characteristic in ['Chaotic']):
        fantastic_chance *= 1.05
        shocking_chance *= 1.05

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
            race_strategy = 10
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.15
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 1.05
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.85
        elif strategy_value < 0.3:
            race_strategy = -30
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15
        else:
            race_strategy = -20
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15

    if team.strategist == "Poor":
        fantastic_chance *= random.uniform(0.925, 0.975)
        shocking_chance *= random.uniform(1.025, 1.075)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.9:
            race_strategy = 15
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.15
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 1.05
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.85
        elif strategy_value < 0.3:
            race_strategy = -25
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15
        else:
            race_strategy = -15
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15

    if team.strategist == "Fair":
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.75:
            race_strategy = 20
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.15
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 1.05
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.85
        elif strategy_value < 0.25:
            race_strategy = -20
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15
        else:
            race_strategy = -10
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15

    if team.strategist == "Great":
        fantastic_chance *= random.uniform(1.025, 1.075)
        shocking_chance *= random.uniform(0.925, 0.975)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.7:
            race_strategy = 25
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.15
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 1.05
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.85
        elif strategy_value < 0.1:
            race_strategy = -15
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15
        else:
            race_strategy = -5
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15

    if team.strategist == "Excellent":
        fantastic_chance *= random.uniform(1.075, 1.125)
        shocking_chance *= random.uniform(0.875, 0.925)
        strategy_value = random.uniform(0, 1)
        if strategy_value > 0.7:
            race_strategy = 30
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 1.15
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 1.05
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 0.85
        elif strategy_value < 0.1:
            race_strategy = -10
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15
        else:
            race_strategy = 0
            if any(trait in driver.traits for trait in ['Strategist']):
                race_strategy *= 0.85
            if any(trait in driver.traits for trait in ['GoodInstincts']):
                race_strategy *= 0.95
            if any(trait in driver.traits for trait in ['PoorCommunicator']):
                race_strategy *= 1.15

    if weather_condition == 'Clear':
        randomness = random.uniform(-24, 24)
        if random.uniform(0, 1) < fantastic_chance:  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < shocking_chance:  # Chance for shocking race
            driver.shocking_race = True

    elif weather_condition == 'Rainy':
        race_strategy *= 1.25
        randomness = random.uniform(-36, 36)
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
        randomness = random.uniform(-48, 48)
        if random.uniform(0, 1) < (fantastic_chance * 5):  # Chance for fantastic race
            driver.fantastic_race = True
        if random.uniform(0, 1) < (shocking_chance * 5):  # Chance for shocking race
            driver.shocking_race = True

    special_modifier = 1
    if driver.fantastic_race:
        print(f"{driver.name} Fantastic Race")
        if random.uniform(0, 1) < 0.75:
            special_modifier *= 1.15
            if random.uniform(0, 1) < 0.5:
                print(f"{driver.name} Even More Fantastic Race")
                special_modifier *= 1.1
                if random.uniform(0, 1) < 0.25:
                    print(f"{driver.name} EVEN MORE FANTASTIC RACE")
                    special_modifier *= 1.05
        else:
            special_modifier *= 1.15

    if driver.shocking_race:
        print(f"{driver.name} Shocking Race")
        if random.uniform(0, 1) < 0.75:
            special_modifier *= 0.85
            if random.uniform(0, 1) < 0.5:
                print(f"{driver.name} Even More Shocking Race")
                special_modifier *= 0.9
                if random.uniform(0, 1) < 0.25:
                    print(f"{driver.name} EVEN MORE SHOCKING RACE")
                    special_modifier *= 0.95
        else:
            special_modifier *= 0.85

    # Calculate penalty factor / randomness based on starting position
    if circuit_type in ['Superspeedway']:
        penalty_factor = (starting_position - (starting_position * 0.25)) * 4.5
        randomness *= 1.7
    elif circuit_type in ['Oval']:
        penalty_factor = (starting_position - (starting_position * 0.25)) * 5.5
        randomness *= 1.5
    elif circuit_type in ['Short Track']:
        penalty_factor = (starting_position - (starting_position * 0.25)) * 6.5
        randomness *= 1.35
    elif circuit_type in ['Road Course', 'Grand Prix']:
        penalty_factor = (starting_position - (starting_position * 0.25)) * 7
    elif circuit_type in ['Street Track']:
        penalty_factor = (starting_position - (starting_position * 0.25)) * 8
    else:
        penalty_factor = (starting_position - (starting_position * 0.25)) * 7
    
    if discipline == 'StockCar':
        randomness *= 1.15
    
    if any(t_characteristic in track_characteristics for t_characteristic in ['Tame']):
        randomness *= 0.8
    
    if any(t_characteristic in track_characteristics for t_characteristic in ['Chaotic']):
        randomness *= 1.2

    race_result = ((((driver.speed / 2) + driver.skill) * 0.75) * special_modifier) + (team.performance * (1 - (0.75 * team.wear))) + team.power + race_strategy + randomness
    race_result -= penalty_factor # Better starting position gives a performance boost

    # Reset the driver's skill to its original value
    driver.skill = original_skill
    driver.speed = original_speed

    driver.fantastic_race = False
    driver.shocking_race = False

    return race_result

# def simulate_race_incident(driver, team):
#     skill_to_speed_difference = (driver.skill - driver.speed) / 100
#     incident_probability = min(max(0.65 + incident_probability, 0), 0.999)

def simulate_retirement(driver, team, starting_position, qualifying_results):
    num_drivers = len(qualifying_results)
    top_30 = int(num_drivers * 0.3)

    # Clamp team.reliability to be at most 1
    reliability = min((team.reliability - team.wear), 0.999)
    threshold = 0.525

    if any(status in team.status for status in ['StartAndPark']) and starting_position > top_30:
        reliability *= 0.15
        threshold *= 0.15

    if random.uniform(0, 1) > reliability:
        if random.uniform(0, 1) > threshold:
            return "Retirement"
        else:
            return ""
    else:
        return ""

def simulate_crash(driver):
    skill_to_speed_difference = (driver.skill - driver.speed) / 100
    crash_probability = min(max(0.65 + skill_to_speed_difference, 0), 0.999)

    # Compare random values with probabilities derived from driver skill and crash probability
    if random.uniform(0, 1) > min(driver.skill / 100, 0.999) and random.uniform(0, 1) > crash_probability:
        if random.uniform(0, 1) < 0.35:
            return "Crash"
        else:
            return ""
    else:
        return ""

def simulate_collision(sorted_qualifying_results):
    # List to store the drivers involved in collisions
    collided_drivers = []

    # Iterate over the sorted qualifying results to check for proximity and collision chances
    for i, ((team_name, driver_name), (driver, qualifying_result)) in enumerate(sorted_qualifying_results):
        # Proximity threshold: Assume a driver is at risk of collision if they are within 3 positions
        proximity_candidates = []
        
        for j in range(i + 1, len(sorted_qualifying_results)):
            if abs(i - j) <= 3:
                proximity_candidates.append(j)

        # Randomly select one or more `j` from the candidates, if any
        if proximity_candidates:
            num_collisions = min(4, len(proximity_candidates))
            weights = [0.5, 0.2, 0.1, 0.05][:num_collisions]
            selected_js = random.sample(proximity_candidates, k=random.choices(range(1, num_collisions + 1), weights=weights)[0])

            for selected_j in selected_js:
                _, (other_driver, _) = sorted_qualifying_results[selected_j]

                # Simulate a collision chance
                skill_to_speed_difference = (driver.skill - driver.speed) / 100
                crash_probability = min(max(0.65 + skill_to_speed_difference, 0), 0.999)

                # If a collision occurs (chance is met), mark both drivers as involved
                if random.uniform(0, 1) > min(driver.skill / 100, 0.999) and random.uniform(0, 1) > crash_probability:
                        if driver.dnf == "" and other_driver.dnf == "":  # Avoid marking the driver multiple times
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
            laps_led[driver] += int(base_laps + (1 - position_factor) * (total_laps / 2) + race_result_factor - random.uniform(-15, 30))
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
                charter_system = row['Charter']  # Static / Dynamic / None
                charter_slots = row['Slots']  # Number of charter slots available
                return discipline, region, tier, team_rules, chassis_rules, engine_rules, charter_system, charter_slots

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

def set_year(year):
    year = "2010"
    return year

def main():
    # Get the directory path of the script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Get the filename without extension
    script_filename = os.path.splitext(os.path.basename(__file__))[0]

    # Assuming the series_name is derived directly from the script filename
    series_name = script_filename.split(" - ")[-1]  # Adjust this based on your filename format

    # Extract parts from the CSV file
    discipline, region, tier, team_rules, chassis_rules, engine_rules, charter_system, charter_slots = get_series_attributes_from_csv(series_name, script_directory)

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
                    row['Sponsor'],     # Sponsor
                    row['Branding'],    # Sponsor
                    row['Commitment'],  # Sponsor
                    row['Chassis'],
                    row['Performance'],
                    row['Aero'],
                    row['Gearbox'],
                    row['Suspension'],
                    row['Brakes'],
                    row['Reliability'],
                    row['Characteristics'],
                    row['Wear'],
                    row['Supplier'],
                    row['Power'],
                    row['Tires'],
                    row['Strategist']
                )

            # Update color after ensuring team exists in the dictionary
            if teams[team_name].commitment.split("|")[0] == "Title":
                color_name = row['Branding']
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
                row['Speed'],
                row['Skill'],
                row['Experience'],
                row['Morale'],
                row['Discipline'],
                row['Preference'],
                row['Traits'],
                row['Fame'],
                row['Reputation'],
                row['Partner'],
                row['Contract'],
                row['Target'],
                row['Relations'],
                team_name
            )
            
            teams[team_name].add_driver(driver)
            drivers.append(driver)

    # Construct the schedule CSV file path
    schedule_csv_path = os.path.join(script_directory, "Schedules", f"{script_filename}.csv")

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

    print(f"\n(Round {order}: {circuit} - {circuit_type} - {int(total_laps)} laps)\n")
    print(f"Weather: {weather_condition}")
    print(f"Lap Record: {lap_record}")

    # Wait for user input before displaying qualifying results
    # input("\n...")

    time.sleep(0.75)  # Add a delay between each entry

    # Calculate team average attributes before qualifying
    for team in teams.values():
        calculate_team_average_attributes(team, discipline)

    # Qualifying
    qualifying_results = {}
    for team in teams.values():
        for driver in team.drivers:
            result = simulate_qualifying(team, weather_condition, discipline, event, grid_size, circuit_type, series_name, script_directory, track_speed, track_characteristics)
            
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
        if team.charter == "":
            # Move driver to sorted_qualifying_results
            sorted_qualifying_results.append(driver)
            dnq_results.remove(driver)

    # Ensure grid size limit is maintained
    while len(sorted_qualifying_results) > grid_size:
        # Move the lowest driver to dnq_results, but ensure drivers with empty team.charter are not moved
        for i in range(len(sorted_qualifying_results) - 1, -1, -1):
            team_name, driver_name = sorted_qualifying_results[i][0]
            team = teams[team_name]
            if team.charter != "":
                dnq_results.append(sorted_qualifying_results.pop(i))
                break

    # Sort the DNQ results by time
    dnq_results = sorted(dnq_results, key=lambda x: x[1][1], reverse=True)

    # Race
    race_results = []
    position_changes = []
    for i, ((team_name, driver_name), _) in enumerate(sorted_qualifying_results):
        team = teams[team_name]
        starting_position = i + 1
        if team.drivers:  # Check if the team has at least one driver
            race_result = simulate_race(team.drivers[0], team, starting_position, weather_condition, discipline, circuit_type, qualifying_results, sorted_qualifying_results, track_characteristics)
            race_results.append((team_name, driver_name, race_result))
        else:
            pass  # Do nothing if no drivers available for the team

    # Sort race results by performance score after the race
    sorted_race_results = sorted(race_results, key=lambda x: (x[2] != 0, x[2]), reverse=True)

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

            main_team_name, *rest = team_name.split(" - ")

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

            main_team_name, *rest = team_name.split(" - ")

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

    print("\n\n - - - Post-Qualifying News - - - \n")

    for i, ((team_name, driver_name), (driver, qualifying_result)) in enumerate(sorted_qualifying_results): ### DO THIS!
        num_drivers = len(sorted_qualifying_results)
        top_25 = int(num_drivers * 0.25)
        bottom_25 = int(num_drivers * 0.75)

        if i <= top_25:
            if random.uniform(0, 1) < 0.4:  # Adjust the probability as needed
                text = markov.generate("Good Interview", driver_name=driver_name, team_name=team_name)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")

        if i >= bottom_25:
            if random.uniform(0, 1) < 0.2:  # Adjust the probability as needed
                text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")
    
    for i, ((team_name, driver_name), qualifying_result) in enumerate(dnq_results):
        if random.uniform(0, 1) < 0.2:  # Adjust the probability as needed
            text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
            print(f"INTERVIEW - ({driver_name} - DNQ):       '" + text + "'")

    time.sleep(1)  # Add a delay between each entry

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

        main_team_name, *rest = team_name.split(" - ")

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
        main_team_name, *rest = team_name.split(" - ")  # Split team name

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
        line.append(")")

        console.print(line)
        time.sleep(0.5)  # Add delay between each entry

    # Print DNF drivers
    for team_name, driver_name, dnf_reason, supplier, color in dnf_drivers:
        main_team_name, *rest = team_name.split(" - ")  # Split team name

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

        if i <= top_20:
            if random.uniform(0, 1) < 0.1:  # Adjust the probability as needed
                if random.uniform(0, 1) < 0.5:
                    print(f"{driver_name} ({team_name}) has fantastic race.\n")
                else:
                    print(f"{driver_name} ({team_name}) impressed with solid drive.\n")
        if i >= bottom_20:
            if random.uniform(0, 1) < 0.1:  # Adjust the probability as needed
                if random.uniform(0, 1) < 0.5:
                    print(f"{driver_name} ({team_name}) has poor race.\n")
                else:
                    print(f"{driver_name} ({team_name}) had weekend to forget.\n")

            if random.uniform(0, 1) < 0.1:  # Adjust the probability as needed
                if random.uniform(0, 1) < 0.5:
                    print(f"Team unimpressed following poor showing from {driver_name} ({team_name}).\n")
                else:
                    print(f"{driver_name} ({team_name}) argues with team after poor race.\n")

    # Check for injuries for drivers who crashed
    for team_name, driver_name, _, _, _ in dnf_drivers:
        if team_name in teams:
            team = teams[team_name]
            driver = next((driver for driver in team.drivers if driver.name == driver_name), None)
            if driver and driver.dnf == "Crash":
                if random.uniform(0, 1) < 0.1:  # Adjust the probability as needed
                    print(f"{driver_name} ({team_name}) has crashed!\n")
                
                if any(trait in driver.traits for trait in ['ShortTemper']):
                    if random.uniform(0, 1) < 0.25:  # Adjust the probability as needed
                        if random.uniform(0, 1) < 0.5:
                            print(f"Team frustrated with {driver_name} ({team_name}) after crash.\n")
                        else:
                            print(f"{driver_name} ({team_name}) fights with management after crashing out!\n")
                else:
                    if random.uniform(0, 1) < 0.1:  # Adjust the probability as needed
                        if random.uniform(0, 1) < 0.5:
                            print(f"Team not happy with {driver_name} ({team_name}) after crashing in race.\n")
                        else:
                            print(f"{driver_name} ({team_name}) feuds with management after crashing out!\n")

            if driver and driver.dnf == "Crash":
                if any(trait in driver.traits for trait in ['InjuryProne']):
                    if random.uniform(0, 1) < 0.075:  # Adjust the probability as needed
                        print(f"{driver_name} ({team_name}) has been injured in terrifying crash!\n")
                else:
                    if random.uniform(0, 1) < 0.025:  # Adjust the probability as needed
                        print(f"{driver_name} ({team_name}) has been injured in massive crash!\n")

            if driver and driver.dnf == "Retirement":
                if any(trait in driver.traits for trait in ['ShortTemper']):
                    if random.uniform(0, 1) < 0.25:  # Adjust the probability as needed
                        if random.uniform(0, 1) < 0.5:
                            print(f"{driver_name} ({team_name}) angry with team after mechanical failure.\n")
                        else:
                            print(f"{driver_name} ({team_name}) fuming at team following premature end to race.\n")
                else:
                    if random.uniform(0, 1) < 0.1:  # Adjust the probability as needed
                        if random.uniform(0, 1) < 0.5:
                            print(f"{driver_name} ({team_name}) not happy with team after mechanical failure.\n")
                        else:
                            print(f"{driver_name} ({team_name}) angry at team following premature end to race.\n")

    for i, (team_name, driver_name, race_result, _, _) in enumerate(finished_drivers):
        num_drivers = len(finished_drivers)
        top_25 = int(num_drivers * 0.25)
        bottom_25 = int(num_drivers * 0.75)
        if i <= top_25:
            if random.uniform(0, 1) < 0.5:  # Adjust the probability as needed
                text = markov.generate("Good Interview", driver_name=driver_name, team_name=team_name)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")

        if i >= bottom_25:
            if random.uniform(0, 1) < 0.25:  # Adjust the probability as needed
                text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
                print(f"INTERVIEW - ({driver_name} - {i + 1}):       '" + text + "'")
    
    for i, (team_name, driver_name, _, _, _) in enumerate(dnf_drivers):
        if random.uniform(0, 1) < 0.25:  # Adjust the probability as needed
            text = markov.generate("Poor Interview", driver_name=driver_name, team_name=team_name)
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
            {"Position": i + 1, "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].sponsor, "Time": formatted_qualifying_lap_times[i][1]}
            for i, ((team_name, driver_name), qualifying_result) in enumerate(sorted_qualifying_results)
        ],
        "DNQ Drivers": [
            {"Position": i + 1 + grid_size, "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].sponsor, "Time": next(time for name, time in formatted_qualifying_lap_times if name == driver_name)}
            for i, ((team_name, driver_name), qualifying_result) in enumerate(dnq_results)
        ],
        "Race Results": [
            {"Position": i + 1, "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].sponsor, "Time": formatted_race_times[i]}
            for i, (team_name, driver_name, race_result, _, _) in enumerate(finished_drivers)
        ],
        "DNF Drivers": [
            {"Position": "DNF", "Driver": driver_name, "Team": team_name, "Supplier": teams[team_name].supplier, "Sponsor": teams[team_name].sponsor, "Reason": dnf_reason}
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