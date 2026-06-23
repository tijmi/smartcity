import json
import csv
import numpy as np
import math
from pathlib import Path

from Info import grid_size, subtile_amount

class City:

    def __init__(self):
        self.fake_tiles = np.ones(shape=(int(math.sqrt(subtile_amount)) * grid_size[0] + 2, int(math.sqrt(subtile_amount)) * grid_size[1] + 2))
        self.city_data =  np.empty(shape=(int(math.sqrt(subtile_amount)) * grid_size[1] + 2, int(math.sqrt(subtile_amount)) * grid_size[0] + 2), dtype=dict)

    # use this when user choose city
    # receive from hardware
    def update_city(self, city_id):
        with open(Path(__file__).parent / "city_data.json", 'r') as jsonfile:
            data = json.load(jsonfile)

            self.fake_tiles = np.array(data[str(city_id)]['fake_tiles'], dtype=object)
            self.city_data = data[str(city_id)]['city_data']

    def convert_Niels_array(self, arr):
        # Increase array size
        arr = np.repeat(arr, int(math.sqrt(subtile_amount)), axis=0)
        arr = np.repeat(arr, int(math.sqrt(subtile_amount)), axis=1)

        arr = arr[2:-2, 2:-2] # Shave off the extra borders

        return arr
    
    def fill_fake_tiles(self):
        arr = np.empty((10, 8), dtype=object)
        right_values = ["built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low"]
        left_values = ["water", "water", "water", "water", "water", "water", "water", "water", "water", "water"]
        top_values = ["built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low"]
        bottom_values = ["built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low", "built_low"]

        arr[0, :] = top_values      # 10 values
        arr[-1, :] = bottom_values  # 10 values
        arr[:, 0] = left_values     # 8 values
        arr[:, -1] = right_values   # 8 values

        return arr

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

                city_json[city_name] = {
                    'population': int(row['population']),
                    'soil': float(row['soil']),
                    'wind': float(row['wind']),
                    'UA': float(row['UA']),
                }



        with open('city_import_test.json', 'w') as f:
            json.dump(city_json, f, indent=2)

        print(f"Saved: {list(city_json.keys())}")

# Always comment this code:

# city = City()
# with open('city_data.json', 'r') as jsonfile:
#     data = json.load(jsonfile)
#
# # Import data initially
# # data["5"]["city_data"] = np.load('grid_data_Amsterdam.npy', allow_pickle=True).tolist()
#
# # data["0"]["fake_tiles"] = np.genfromtxt('border_Eindhoven.csv', delimiter=',', dtype=None, encoding='utf-8').tolist()
# #
# # data["0"]["fake_tiles"] = city.convert_Niels_array(data["0"]["fake_tiles"]).tolist()
# # data["0"]["fake_tiles"] = np.rot90(data["0"]["fake_tiles"]).tolist()
#
# with open('city_data.json', 'w') as jsonfile:
#     json.dump(data, jsonfile, indent=2)

