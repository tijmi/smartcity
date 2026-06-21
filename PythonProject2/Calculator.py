from Info import type_effect, type_roughness, types, grid_size, subtile_amount
from pathlib import Path
import math
import numpy as np
import json

BASE_DIR = Path(__file__).parent
TILE_TYPES_PATH = BASE_DIR / 'Tile_types.json'

class Calculator:
    def __init__(self):
        self.city = 0
        self.base_temperature = 17 # HAS TO CONTAIN BASE TEMPERATURE CALCULATED
        self.subtiles = np.empty(shape=(int(math.sqrt(subtile_amount)) * grid_size[0], int(math.sqrt(subtile_amount)) * grid_size[1]), dtype=object) # temporary empty list

        with open(TILE_TYPES_PATH, 'r') as jsonfile:
            self.data = json.load(jsonfile)

    def update_calculation(self, city, subtiles, tile_population, tile_soil_sealing, temperature):
        print("updating calculations")
        self.city = city
        self.subtiles = subtiles
        for x in range(grid_size[0] * int(math.sqrt(subtile_amount))):
            for y in range(grid_size[1] * int(math.sqrt(subtile_amount))):
                # For subtile at (X, Y):
                current_subtile = self.subtiles[x, y]
                UHI = self.calc_act_UHI(x, y, tile_population, tile_soil_sealing, temperature)
                current_subtile.UHI = UHI

    def calc_act_UHI(self, x, y, tile_population, tile_soil_sealing, temperature):
        max_UHI = -1.605 + (1.062 * math.log10(self.city.city_data[x][y]["pop_10km"] + tile_population)) - (0.356 * self.calc_wind10m(x, y))
        if max_UHI < 0: max_UHI = 0

        pot_UHI = max_UHI * (self.city.city_data[x][y]["ss_1km"] + tile_soil_sealing) / 100

        type_reduction = self.calc_type_reduction(x, y)
        act_UHI = pot_UHI * (1-type_reduction)

        d_temperature = temperature - self.base_temperature # Get delta temp
        if d_temperature < 0: d_temperature = 0 # Not negative

        act_UHI += 0.079 * temperature * (self.city.city_data[x][y]["ss_1km"] + tile_soil_sealing) # Add effect of temperature

        return act_UHI


    def calc_wind10m(self, x, y):
        windspeed10m = self.city.city_data[x][y]["ws_100m_alt"] * math.log(10 / type_roughness[self.subtiles[x, y].type]) / math.log(100 / type_roughness[self.subtiles[x, y].type])

        return windspeed10m

    def calc_type_reduction(self, x, y):
        corner_tiles = [] # Tiles touching corners with main tile
        side_tiles = [] # Tiles to the sides of main tile
        self.fake_tiles = np.ones(shape=(int(math.sqrt(subtile_amount)) * grid_size[0] + 2, int(math.sqrt(subtile_amount)) * grid_size[1] + 2))
        fake_tiles = self.city.fake_tiles
        type_coverage30m = { # Temp empty version
            "built_low": 0,
            "built_high": 0,
            "trees": 0,
            "low_veg": 0,
            "water": 0,
            "farmland": 0,
            "bare_soil": 0,
            "built_low_char": 0,
            "built_high_char": 0,
            "appartment_char": 0,
            "canals_char": 0,
            "lakes_char": 0,
            "parks_char": 0,
            "forests_char": 0,
            "farmland_char": 0
        }

        # Gather all the types corner- and side-connected neighbours
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i == x and j == y:
                    continue  # Skip center

                is_side = (i == x) or (j == y)  # Same row or column, not diagonal

                try:
                    tile = self.subtiles[i, j]

                    if is_side:
                        side_tiles.append(tile.type)
                    else:
                        corner_tiles.append(tile.type)
                except:
                    tile_type = fake_tiles[i + 1, j + 1]

                    if is_side:
                        side_tiles.append(tile_type)
                    else:
                        corner_tiles.append(tile_type)

        # Note how much each type covers the area. Totals to 100
        for tile_type in corner_tiles:
            if tile_type in types: type_coverage30m[tile_type] += 7.71
        for tile_type in side_tiles:
            if tile_type in types: type_coverage30m[tile_type] += 13.74
        type_coverage30m[self.subtiles[x, y].type] += 14.2

        # Calculate type reduction
        total = 0
        for type in types:
            total += (type_coverage30m[type] / 100) * type_effect[type]

        return total