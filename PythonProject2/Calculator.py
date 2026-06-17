from Info import type_effect, type_roughness, types, grid_size, subtile_amount
import math
import numpy as np


class Calculator:
    def __init__(self):
        self.city = None
        self.subtiles = np.empty(shape=(int(math.sqrt(subtile_amount)) * grid_size[0], int(math.sqrt(subtile_amount)) * grid_size[1]), dtype=object) # temporary empty list

    def update_calculation(self, city, subtiles):
        self.city = city
        self.subtiles = subtiles
        for x in range(grid_size[0] * int(math.sqrt(subtile_amount))):
            for y in range(grid_size[1] * int(math.sqrt(subtile_amount))):
                # For subtile at (X, Y):
                current_subtile = self.subtiles[x, y]
                UHI = self.calc_act_UHI(x, y)
                current_subtile.UHI = UHI

    def calc_act_UHI(self, x, y):
        max_UHI = -1.605 + (1.062 * math.log10(self.city.population)) - (0.356 * self.calc_wind10m(x, y))
        pot_UHI = abs(max_UHI) * self.city.soil_sealing
        type_reduction = self.calc_type_reduction(x, y)
        act_UHI = pot_UHI * (1-type_reduction)

        return act_UHI


    def calc_wind10m(self, x, y):
        windspeed10m = self.city.wind[x, y] * math.log(10 / type_roughness[self.subtiles[x, y].type]) / math.log(100 / type_roughness[self.subtiles[x, y].type])

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

        # Gather all the types corner- and side-connected neighbours
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i == x and j == y:
                    continue  # skip center

                try:
                    tile = self.subtiles[i, j]
                    is_side = (i == x) or (j == y)  # same row or column, not diagonal

                    if is_side:
                        side_tiles.append(tile.type)
                    else:
                        corner_tiles.append(tile.type)
                except:
                    pass # Skipped empty ghost tiles

        # Note how much each type covers the area. Totals to 100
        for tile_type in corner_tiles:
            if tile_type in types: type_coverage30m[tile_type] += 7.71
            else: print("Oh no! It looks like someone made a type typo, how sad!")
        for tile_type in side_tiles:
            if tile_type in types: type_coverage30m[tile_type] += 13.74
            else: print("Oh no! It looks like someone made a type typo, how sad!")
        type_coverage30m[self.subtiles[x, y].type] += 14.2

        print(type_coverage30m)

        # Calculate type reduction
        total = 0
        for type in types:
            total += (type_coverage30m[type] / 100) * type_effect[type]

        print(total)

        return total