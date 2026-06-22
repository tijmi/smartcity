from Tile import Tile
from Info import grid_size, subtile_amount
import numpy as np
import math
import random

class TileManager:

    def __init__(self):
        # Make empty 2D array
        self.tiles = np.empty(shape=grid_size, dtype=object)
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.tiles[i, j] = Tile((i, j), random.randint(0, 6)) # Place random tile in each position


    def update_tile(self, position, type):

        x = math.floor(position % grid_size[0])
        y = math.floor(position // grid_size[0])

        print(f"tile_location: {x}, {y}")

        self.tiles[x, y] = Tile((x, y), type) # Place new tile

    def get_subtiles(self):
        # Make empty subtiles array
        subtiles = np.zeros(shape=(grid_size[0] * int(math.sqrt(subtile_amount)), (grid_size[1] * int(math.sqrt(subtile_amount)))), dtype= object)

        # add every subtile according to their total_pos
        for tile in self.tiles.flat:
            for subtile in tile.subtiles.flat:
                x = subtile.total_subtile_pos[0]
                y = subtile.total_subtile_pos[1]
                subtiles[x, y] = subtile

        return subtiles
    
    def get_soil_population(self):
        tile_population = 0
        tile_soil_sealing = 0
        for tile in self.tiles.flat:
            tile_population += tile.population
            tile_soil_sealing += tile.soil_sealing
        return tile_soil_sealing, tile_population