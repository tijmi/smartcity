import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from Info import grid_size
from Debugger import debug
from screeninfo import get_monitors

class Heatmap:

    def __init__(self, screen_index=0, display_tile_type=False, screeninfo=None):
        self.display_tile_type = display_tile_type

        # ---------------------------------------------------------------------
        # Remove the toolbar
        plt.rcParams['toolbar'] = 'None'

        # Create the figure (window) and axis (plot)
        self.fig, self.axis = plt.subplots()

        # Set the axis to fill the figure completely and turn off the axis drawing
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.axis.set_axis_off()

        # Move the window to the specific screen and set it to fullscreen
        monitors = get_monitors()
        target = monitors[screen_index]
        debug(f"window.wm_geometry(+{target.x}+{target.y})")
        manager = plt.get_current_fig_manager()

        manager.window.wm_geometry(f"{target.width}x{target.height}+{target.x}+{target.y}")
        plt.pause(0.1)
        # manager.window.wm_overrideredirect(True)

        # Set the backgrounds to black
        self.fig.patch.set_facecolor('black')
        self.axis.set_facecolor('black')

        # ---------------------------------------------------------------------
        # Wait to finish resizing the window, then get the height of the screen
        plt.pause(0.1)
        screen_h = self.fig.canvas.get_width_height()[1]

        total_cols = 72
        total_rows = 90

        # Compute the tile size in pixels (height is limiting, portrait grid in a landscape window)
        subtile_side_length = round(screen_h / total_rows)
        border_length = subtile_side_length * 9

        # Compute the window width and height for consistent and proportional sizes
        self.display_w, self.display_h = total_cols * subtile_side_length, total_rows * subtile_side_length

        # Create the image extent
        self.extent_image = [0, self.display_w, self.display_h, 0]
        # Create the grid extent, leaving a 9 tiles border around it
        self.extent = [border_length, self.display_w - border_length, self.display_h - border_length, border_length]

        # Lock the axes limits so the border margin is preserved
        self.axis.set_xlim(0, self.display_w)
        self.axis.set_ylim(self.display_h, 0)

        # Calculate the size of full tiles ( 9x9 subtiles )
        grid_rows, grid_cols = 8, 6
        x0, x1, y1, y0 = self.extent  # left, right, bottom, top
        tile_w = (x1 - x0) / grid_cols
        tile_h = (y1 - y0) / grid_rows

        # Calculate the center coordinates for each tile
        self.full_tile_centers = np.array([
            (x0 + (col + 0.5) * tile_w, y0 + (row + 0.5) * tile_h)
            for row in range(grid_rows)
            for col in range(grid_cols)
        ])
        # ---------------------------------------------------------------------
        # Layer 1: city border
        placeholder_border = np.zeros((self.display_h, self.display_w, 3), dtype=np.uint8)
        self.city_border_night = self.axis.imshow(placeholder_border, origin='upper', zorder=0)
        self.city_border_day = self.axis.imshow(placeholder_border, origin='upper', zorder=0)

        # ---------------------------------------------------------------------
        # Layer 2: heatmap overlay
        placeholder_grid = np.zeros((total_rows, total_cols, 1), dtype=np.float16)
        self.heatmap = self.axis.imshow(
            placeholder_grid,
            extent=self.extent,
            interpolation='catrom',
            cmap="RdYlGn_r",
            vmin=0, vmax=3,
        )

        # ---------------------------------------------------------------------
        # Layer 3: tile type overlay
        if display_tile_type:

            # placeholder values
            placeholder_grid2 = np.zeros(grid_rows * grid_cols)

            cmap = matplotlib.colors.ListedColormap([
                'blue',  # 0: empty/low_veg
                'pink',  # 1: suburbs
                'red',  # 2: built_high
                'teal',  # 3: water
                'teal',  # 3: water
                'purple',  # 4: low_veg
                'green',  # 5: trees
                'yellow',  # 6: farm
                'pink',  # 7: player_built_low
                'red',  # 8: player_built_high
                'red',  # 9: player_apartment
                'teal',  # 10: player_canals
                'teal',  # 11: player_lakes
                'purple',  # 12: player_parks
                'green',  # 13: player_forest
                'yellow',  # 14: player_farm
            ])

            self.scatter = self.axis.scatter(
                self.full_tile_centers[:, 0],  # x
                self.full_tile_centers[:, 1],  # y
                c=placeholder_grid2,  # values
                cmap=cmap,
                vmin=0, vmax=14,
                s=400,  # marker size
                marker='o',  # circle
                zorder=2,
            )

        # ---------------------------------------------------------------------
        # Layer 4: player spotlight overlay
        self.spotlight = self.axis.scatter(
            [self.full_tile_centers[0, 0]],  # placeholder x
            [self.full_tile_centers[0, 1]],  # placeholder y
            s=(border_length*border_length) * 0.5,  # Border length = tile length, already computed
            alpha=0.0,  # hidden at start
            facecolors=None,
            zorder=3,
            linewidths=3,  # stroke width
            edgecolors='black',  # stroke color
        )

        # ---------------------------------------------------------------------
        # Set the plot as interactive, allowing updates and show the plot
        plt.ion()
        plt.show()

    def update_border(self, new_border):
        self.city_border_day.set_data(new_border["day"].data)
        self.city_border_night.set_data(new_border["night"].data)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def update_grid(self, new_grid):
        smoothed = new_grid #gaussian_filter(new_grid, sigma=2.5)
        self.heatmap.set_data(smoothed)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def set_time(self, time_hour):
        alpha = 1 - ((1 + np.tanh(3 * np.cos(0.2625 * (time_hour - 1)))) / 2)
        self.city_border_day.set_alpha(alpha)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def update_grid_ids(self, new_grid):
        if self.display_tile_type:
            self.scatter.set_array(new_grid.flatten())
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def set_spotlight(self, tile_index):
        row_major_idx = (tile_index % grid_size[0]) * grid_size[1] + (tile_index // grid_size[0])
        x, y = self.full_tile_centers[row_major_idx]
        self.spotlight.set_offsets([[x, y]])
        self.spotlight.set_alpha(1.0)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def clear_spotlight(self):
        self.spotlight.set_alpha(0.0)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    @property
    def size(self):
        return self.display_w, self.display_h
