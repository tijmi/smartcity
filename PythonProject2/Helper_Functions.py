import random
import Info
import numpy as np


def get_tile_population(type):
    if type == "built_low" or type == "built_low_char": 
        return 7
    elif type == "built_high" or type == "built_high_char" or type == "appartment_char": 
        return 10
    else: return 0


def get_tile_soil_sealing(type):
    if type == "built_low" or type == "built_low_char": 
        return 0.0127
    elif type == "built_high" or type == "built_high_char" or type == "appartment_char": 
        return 0.0127
    else: return 0


def create_fake_input(state, state_lock):
    # Update for queue
    pass


# Needs tile_manager,calculator, heatmap, info
def update_grid(ctx, tile_id):
    all_subtiles = ctx.tile_manager.get_subtiles()
    ctx.calculator.update_calculation(ctx.city, all_subtiles, ctx.tile_manager.get_soil_population()[1], ctx.tile_manager.get_soil_population()[0])
    uhi_array = np.vectorize(lambda subtile: subtile.UHI)(all_subtiles)
    ctx.heatmap.update_grid(uhi_array)

    if Info.use_type_dots:
        get_type = np.vectorize(lambda tile: tile.type_id)
        type_array = get_type(ctx.tile_manager.tiles)
        ctx.heatmap.update_grid_ids(type_array)

    return uhi_array