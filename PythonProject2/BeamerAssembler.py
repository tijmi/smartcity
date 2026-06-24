import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

class Heatmap:

    def __init__(self):
        from screeninfo import get_monitors

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
        target = monitors[0]
        print(f"window.wm_geometry(+{target.x}+{target.y})")
        manager = plt.get_current_fig_manager()

        manager.window.wm_geometry(f"{target.width}x{target.height}+{target.x}+{target.y}")
        plt.pause(0.1)
        manager.window.wm_overrideredirect(True)

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
        tile_side_length = round(screen_h / total_rows)
        border_length = tile_side_length * 9

        # Compute the window width and height for consistent and proportional sizes
        self.display_w, self.display_h = total_cols * tile_side_length, total_rows * tile_side_length

        # Create the image extent
        self.extent_image = [0, self.display_w, self.display_h, 0]
        # Create the grid extent, leaving a 9 tiles border around it
        self.extent = [border_length, self.display_w - border_length, self.display_h - border_length, border_length]

        # Lock the axes limits so the border margin is preserved
        self.axis.set_xlim(0, self.display_w)
        self.axis.set_ylim(self.display_h, 0)

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
            cmap="Oranges",
            vmin=0, vmax=4,
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
        smoothed = gaussian_filter(new_grid, sigma=2.5)
        self.heatmap.set_data(smoothed)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def set_time(self, time_hour):
        alpha = 1 - ((1 + np.tanh(3 * np.cos(0.2625 * (time_hour - 1)))) / 2)
        self.city_border_day.set_alpha(alpha)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    @property
    def size(self):
        return self.display_w, self.display_h
