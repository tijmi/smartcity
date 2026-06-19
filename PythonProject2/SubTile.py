from Info import subtile_amount
import math
class Subtile:

    def __init__(self, type, subtile_pos, tile_pos):
        self.type = type
        self.subtile_pos = subtile_pos
        self.total_subtile_pos = self.get_total_subtile(tile_pos)
        self.UHI = 0

        self.population = 0
        self.soil_sealing = 0
        if type == "built_low" or type == "built_low_char": 
            self.population = 7
            self.soil_sealing = 0.128
        if type == "built_high" or type == "built_high_char" or type == "appartment_char": 
            self.population = 10
            self.soil_sealing = 0.128

    def get_total_subtile(self, tile_pos):
        s_amount = int(math.sqrt(subtile_amount))
        x = (tile_pos[0] * s_amount) + self.subtile_pos[0]
        y = (tile_pos[1] * s_amount) + self.subtile_pos[1]

        total_pos = (x, y)
        return total_pos