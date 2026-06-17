from Info import subtile_amount
import math
class Subtile:

    def __init__(self, type, subtile_pos, tile_pos):
        self.type = type
        self.subtile_pos = subtile_pos
        self.total_subtile_pos = self.get_total_subtile(tile_pos)
        self.UHI = 0

        self.population = 0
        if type == "built_low": self.population = 4
        if type == "built_high": self.population = 10

    def get_total_subtile(self, tile_pos):
        s_amount = int(math.sqrt(subtile_amount))
        x = (tile_pos[0] * s_amount) + self.subtile_pos[0]
        y = (tile_pos[1] * s_amount) + self.subtile_pos[1]

        total_pos = (x, y)
        return total_pos