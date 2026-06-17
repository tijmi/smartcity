import matplotlib.pyplot as plt
import numpy as np
from Info import grid_size, subtile_amount
import math
class Heatmap_Creator:

    def __init__(self):
        # Turn on interactive mode, for real-time update
        plt.ion()
        self.subtiles = []


    def update_heatmap(self, subtiles):
        s = int(math.sqrt(subtile_amount))
        rows = grid_size[0]*s
        cols = grid_size[1]*s

        # extract UHI value from each subtile into a 2D array
        uhi_grid = np.zeros((rows, cols))
        for x in range(rows):
            for y in range(cols):
                uhi_grid[x,y] = subtiles[x,y].UHI

        # clear previous frame and redraw heatmap
        plt.clf()
        plt.imshow(
            uhi_grid,
            cmap = "RdYlGn_r",# Green(Low) to Red(High)
            vmin = 0, vmax = 3.0,# UHI range
            interpolation= "bilinear" # smooth blending between tile edges
        )
        plt.colorbar(label = "UHI (°C)")
        plt.axis("off")
        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)
        plt.savefig("PythonProject2/heatmap.png")
