from collections import deque
from Debugger import debug


class PlayerLocation:
    def __init__(self):
        self.location_buffer = deque(maxlen=10)

    def new_location(self, tile_id):
        self.location_buffer.append(tile_id) # Add the newest location
        debug(f"New player location: {tile_id}", "PLAYER_DEBUG")

    def remove_location(self, tile_id):
        if tile_id in self.location_buffer:
            self.location_buffer.remove(tile_id)
            debug(f"Removed player location: {tile_id}", "PLAYER_DEBUG")

    def get_latest_location(self):
        debug(f"Player location to display: {self.location_buffer[-1]}", "PLAYER_DEBUG")
        return self.location_buffer[-1]
