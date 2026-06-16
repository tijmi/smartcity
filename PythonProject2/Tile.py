from SubTile import Subtile
from Info import subtile_amount
import math
import numpy as np
import json

class Tile:

    def __init__(self, grid_pos, type):
        self.grid_pos = grid_pos
        self.type = 0
        self.subtiles = np.empty(shape=(int(math.sqrt(subtile_amount)), int(math.sqrt(subtile_amount))), dtype=object)

        self.update_tile(type)

        # Example of getting population
        self.population = 0
        if type == "built_low": self.population = 4
        if type == "built_high": self.population = 10

    def update_tile(self, type):

        with open('Tile_types.json', 'r') as jsonfile:
            data = json.load(jsonfile)

            self.type = data[str(type)]

        # Generate subtiles
        for x in range(int(math.sqrt(subtile_amount))):
            for y in range(int(math.sqrt(subtile_amount))):
                self.subtiles[x, y] = Subtile(self.type, (x, y), self.grid_pos)