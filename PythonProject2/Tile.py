from SubTile import Subtile
from Info import subtile_amount
from pathlib import Path
import math
import numpy as np
import json

BASE_DIR = Path(__file__).parent
TILE_TYPES_PATH = BASE_DIR / 'Tile_types.json'

class Tile:

    def __init__(self, grid_pos, type):
        self.grid_pos = grid_pos
        with open(TILE_TYPES_PATH, 'r') as jsonfile:
            data = json.load(jsonfile)

            self.type = data[str(type)]

        self.population = 0
        self.soil_sealing = 0

        # Generate subtiles
        self.subtiles = np.empty(shape=(int(math.sqrt(subtile_amount)), int(math.sqrt(subtile_amount))), dtype=object)
        for x in range(int(math.sqrt(subtile_amount))):
            for y in range(int(math.sqrt(subtile_amount))):
                self.subtiles[x, y] = Subtile(self.type, (x, y), self.grid_pos)
                self.population += self.subtiles[x, y].population
                self.soil_sealing += self.subtiles[x, y].soil_sealing