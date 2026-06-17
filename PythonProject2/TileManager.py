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
                self.tiles[i, j] = Tile((i, j), random.randint(0, 7))

        self.tile_population = 0


    def update_tile(self, position, type):

        x = int(position % grid_size[0])
        y = int(position // grid_size[1])

        print(x, y)

        self.tile_population -= self.tiles[x, y].population # Remove population addition of that tile
        self.tiles[x, y] = Tile((x, y), type)
        self.tile_population += self.tiles[x, y].population # Add population of that tile

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