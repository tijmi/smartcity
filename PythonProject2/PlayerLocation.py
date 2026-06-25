from collections import deque


class PlayerLocation:
    def __init__(self):
        self.location_buffer = deque(maxlen=10)

    def new_location(self, tile_id):
        self.location_buffer.append(tile_id) # Add the newest location
        print(self.location_buffer)

    def remove_location(self, tile_id):
        self.location_buffer.remove(tile_id)
        print(self.location_buffer)

    def get_latest_location(self):
        return self.location_buffer[-1]