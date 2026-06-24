

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