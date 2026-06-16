class Heatmap_Creator:

    def __init__(self):
        self.subtiles = []


    def update_heatmap(self, subtiles):
        # Replace all subtiles with their UHI
        for array in subtiles:
            for tile in array:
                tile = tile.UHI

        # Make a visual map out of it for the beamer to display
        pass