from Tile import Tile
from Info import grid_size, subtile_amount
import numpy as np
import math

class TileManager:

    def __init__(self):
        # Make empty 2D array
        self.tiles = np.empty(shape=grid_size)
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.tiles[i, j] = Tile((i, j), 1)


    def update_tile(self, position, type):
        tile = self.tiles[position]
        tile.update_tile(type)

    def get_subtiles(self):
        # Make empty subtiles array
        subtiles = np.zeros(shape=(grid_size[0] * math.sqrt(subtile_amount), (grid_size[1] * math.sqrt(subtile_amount))))

        # add every subtile according to their total_pos
        for tile in self.tiles:
            for subtile in tile.subtiles:
                x = subtile.total_subtile_pos[0]
                y = subtile.total_subtile_pos[1]
                subtiles[x, y] = subtile

        return subtiles