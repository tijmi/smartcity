from Info import type_effect, type_roughness, types, grid_size, subtile_amount
import math
import numpy as np
import json


class Calculator:
    def __init__(self):
        self.city = 0
        self.subtiles = np.empty(shape=(int(math.sqrt(subtile_amount)) * grid_size[0], int(math.sqrt(subtile_amount)) * grid_size[1]), dtype=object) # temporary empty list

    def update_calculation(self, city, subtiles, tile_population, tile_soil_sealing):
        self.city = city
        self.subtiles = subtiles
        for x in range(grid_size[0] * int(math.sqrt(subtile_amount))):
            for y in range(grid_size[1] * int(math.sqrt(subtile_amount))):
                # For subtile at (X, Y):
                current_subtile = self.subtiles[x, y]
                UHI = self.calc_act_UHI(x, y, tile_population, tile_soil_sealing)
                print(UHI)
                current_subtile.UHI = UHI

    def calc_act_UHI(self, x, y, tile_population, tile_soil_sealing):
        max_UHI = -1.605 + (1.062 * math.log10(self.city.population + tile_population)) - (0.356 * self.calc_wind10m(x, y))
        # max_UHI = -1.605 + (1.062 * math.log10(self.city.city_data[x, y]["population"] + tile_population)) - (0.356 * self.calc_wind10m(x, y))
        if max_UHI < 0: max_UHI = 0

        pot_UHI = max_UHI * (self.city.soil_sealing + tile_soil_sealing) / 100

        # pot_UHI = max_UHI * (self.city.city_data[x, y]["soil_sealing"] + tile_soil_sealing) / 100

        type_reduction = self.calc_type_reduction(x, y)
        act_UHI = pot_UHI * (1-type_reduction)

        return act_UHI


    def calc_wind10m(self, x, y):
        windspeed10m = self.city.wind * math.log(10 / type_roughness[self.subtiles[x, y].type]) / math.log(100 / type_roughness[self.subtiles[x, y].type])

        # windspeed10m = self.city.city_data[x, y]["wind"] * math.log(10 / type_roughness[self.subtiles[x, y].type]) / math.log(100 / type_roughness[self.subtiles[x, y].type])

        return windspeed10m

    def calc_type_reduction(self, x, y):
        corner_tiles = [] # Tiles touching corners with main tile
        side_tiles = [] # Tiles to the sides of main tile
        fake_tiles = self.city.fake_tiles
        type_coverage30m = { # Temp empty version
            "built_low": 0,
            "built_high": 0,
            "trees": 0,
            "shrubs": 0,
            "low_veg": 0,
            "water": 0,
            "farmland": 0,
            "bare_soil": 0
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
                    tile_type = fake_tiles[i+ 1, j+ 1]

                    with open('PythonProject2/Tile_types.json', 'r') as jsonfile:
                        data = json.load(jsonfile)

                        tile_type = data[str(int(tile_type))]

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

        print(f"coordinates: {x, y} this {type_coverage30m}")

        # Calculate type reduction
        total = 0
        for type in types:
            total += (type_coverage30m[type] / 100) * type_effect[type]

        return total