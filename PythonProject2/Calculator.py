from Info import type_effect, type_roughness, types, grid_size
import math
import numpy as np


class Calculator:
    def __init__(self):
        self.city = None
        self.subtiles = np.zeros((1, 1)) # temporary empty list

    def update_calculation(self, city, subtiles):
        self.city = city
        self.subtiles = subtiles
        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                # For subtile at (X, Y):
                current_subtile = self.subtiles[x, y]
                current_subtile.update_UHI(self.calc_act_UHI(x, y))

    def calc_act_UHI(self, x, y):
        max_UHI = abs(-1.605 + (1.062 * math.log10(self.city.population10km)) - (0.356 * self.calc_wind10m(x, y)))
        pot_UHI = max_UHI * self.city.soil_sealing1km
        type_reduction = self.calc_type_reduction(x, y)
        act_UHI = pot_UHI * (1-type_reduction)

        return act_UHI


    def calc_wind10m(self, x, y):
        windspeed10m = self.city.wind[x][y] * math.log(10 / type_roughness[self.subtiles[x, y].type]) / math.log(100 / type_roughness[self.subtiles[x, y].type])

        return windspeed10m

    def calc_type_reduction(self, x, y):
        corner_tiles = [] # Tiles touching corners with main tile
        side_tiles = [] # Tiles to the sides of main tile
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

        # Gather all the types corner- and side-connected
        for i in range(x - 1, x + 1):
            for j in range(y - 1, y + 1):
                tile = self.subtiles[i, j]

                if i == 0 or j == 0:
                    side_tiles.append(tile.type)
                elif i != 0 and j != 0:
                    corner_tiles.append(tile.type)

        # Note how much each type covers the area
        for tile_type in corner_tiles:
            if tile_type in types: type_coverage30m[tile_type] += 7.71
            else: print("Oh no! It looks like someone made a type typo, how sad!")
        for tile_type in side_tiles:
            if tile_type in types: type_coverage30m[tile_type] += 13.74
            else: print("Oh no! It looks like someone made a type typo, how sad!")
        type_coverage30m[self.subtiles[x, y].type] += 14.2

        # Calculate type reduction
        total = 0
        for type in types:
            total += type_coverage30m[type] * type_effect[type]

        return total