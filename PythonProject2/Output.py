import math
from Info import grid_size, subtile_amount
from Helper_Functions import get_tile_population

def get_player_loc_data(player_pos, city, tile_manager, temperature, death):
    # Get UHI and wind data at player location
    wind_data = city.city_data[player_pos[0]][player_pos[1]]["ws_100m_alt"]

    total_wind = 0

    tile = tile_manager.tiles[player_pos] # Tile of player
    total_UHI = 0
    for subtile in tile.subtiles.flat: # For each subtile within the player's tile
        total_UHI += subtile.UHI # Get subtile UHI
        total_wind += wind_data # Get subtile wind

    # Final data to output
    average_UHI = total_UHI / subtile_amount
    average_wind = total_wind / subtile_amount

    if temperature > 22:
        death_to_UHI = int(death * (0.0284 * average_UHI))
    elif temperature > 16:
        death_to_UHI = int(death * (0.0157 * average_UHI))
    else:
        death_to_UHI = 0

    return average_wind, average_UHI, death_to_UHI

# Collect all player output data and return
def build_player_output(player_id, tile_manager, city, temperature, death):
    if player_id is None:
        return {
            "uhi": 0,
            "wind": 0,
            "land_use": 0,
            "death": 0,
            "city": city.name,
            "population": 0,
            "has_player": False,
            "neighbors": {
                "front": None,
                "left": None,
                "right": None
            }
        }
    
    # Convert tile id to x, y index of array
    x = int(player_id % grid_size[0])
    y = int(player_id // grid_size[0])


    wind, uhi, death_to_UHI = get_player_loc_data((x, y), city, tile_manager, temperature, death)

    tile = tile_manager.tiles[x, y]

    def get_neighbor_type(nx, ny):
        if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
            return tile_manager.tiles[nx, ny].type
        else:
            return city.fake_tiles[nx + 1, ny + 1]
    
    population = 0
    for i in range(x-1, x+2):
        for j in range(y-1, y+2):
            try:
                population += get_tile_population(tile_manager.tiles[i, j].type)
            except:
                population += get_tile_population(city.fake_tiles[(i * int(math.sqrt(subtile_amount))) + 1, j * int(math.sqrt(subtile_amount)) + 1])

    # neighbors: for connect with scene in Unity
    return{
        "uhi": uhi,
        "wind": wind,
        "land_use": tile.type,
        "death": death_to_UHI,
        "city": city.name,
        "population": int(population / 45),
        "has_player": True,
        "neighbors":{
            "front": get_neighbor_type(x-1, y),
            "left": get_neighbor_type(x, y-1),
            "right": get_neighbor_type(x, y+1),
        }
    }