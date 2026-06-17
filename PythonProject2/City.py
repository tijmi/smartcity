import json
import csv
import numpy as np
import math

from Info import grid_size, subtile_amount


class City:

    def __init__(self):
        self.population = 250000
        self.soil_sealing = 87
        # could depend on actual dataset
        self.wind = 7
        self.fake_tiles = np.ones(shape=(int(math.sqrt(subtile_amount)) * grid_size[0] + 2, int(math.sqrt(subtile_amount)) * grid_size[1] + 2))

    # use this when user choose city
    # receive from hardware
    def update_city(self, city_id):
        with open('city_data.json', 'r') as jsonfile:
            data = json.load(jsonfile)

            self.population = data[str(city_id)]['population']
            self.soil_sealing = data[str(city_id)]['soilsealing']
            self.wind = data[str(city_id)]['wind']
            #self.fake_tiles = data[str(city_id)]['fake_tiles']

            print(self.population, self.soil_sealing, self.wind)

    # One time working function for importing actual data to JSON file
    def save_to_json(self, csv_path):
        cities = ["DenHaag", "Middelburg", "Eindhoven", "Groningen", "Veluwe"]
        city_json = {}

        # csv_path/wind need to change based on actual data
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                city_name = row['city']

                if city_name not in cities:
                    print(f"{city_name} is not in cities list, check list first")
                    continue

                city = City()
                city.population = int(row['population'])
                city.soil_sealing = float(row['soil'])
                city.wind = row['wind']

                city_json[city_name] = {
                    'population': city.population,
                    'soil': city.soil_sealing,
                    'wind': city.wind
                }



        with open('city_data.json', 'w') as f:
            json.dump(city_json, f, indent=2)

        print(f"Saved: {list(city_json.keys())}")