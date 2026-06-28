import random
import Info
import numpy as np
from pynput import keyboard

time = 0
fake_tiles = [0] * 48
fake_tiles_exclusive_placed = {v: False for v in range(7, 15)}


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
    else:
        return 0


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


def listen_for_keys(queue):
    with keyboard.Listener(on_press=lambda key: create_fake_webserver_input(key, queue)) as listener:
        listener.join()


def random_available_value():
    available_picks = list(range(0, 7))  # 0-6 are always freely available
    available_picks += [v for v, placed in fake_tiles_exclusive_placed.items() if not placed]
    return random.choice(available_picks)


def fake_tile_event():
    idx = random.randrange(len(fake_tiles))
    current = fake_tiles[idx]

    if current == 0:
        value = random_available_value()
        fake_tiles[idx] = value
        if value in fake_tiles_exclusive_placed:
            fake_tiles_exclusive_placed[value] = True
        return value, idx
    else:
        fake_tiles[idx] = 0
        if current in fake_tiles_exclusive_placed:
            fake_tiles_exclusive_placed[current] = False
        return 0, idx


def create_fake_webserver_input(key, queue):
    try:
        char = key.char
    except AttributeError:
        return  # ignore special keys (shift, ctrl, etc.)

    match char:
        case 't':
            type, id = fake_tile_event()
            data = {"tile_id": id,
                    "tile_type": type
                    }
            fake_webserver_logic(data, queue)
        case 'c':
            data = {"city_id": random.randint(1,10)}
            fake_webserver_logic(data, queue)
        case 'h':
            global time
            time += 1
            data = {"time": time}
            fake_webserver_logic(data, queue)


def fake_webserver_logic(data, event_queue):
    if 'tile_id' in data and 'tile_type' in data:
        if data.get('tile_type') == 0:
            event_queue.put({"event_type": "tile_removed", "data": {
                "tile_id": data.get('tile_id'),
                "tile_type": data.get('tile_type')
            }})
        else:
            event_queue.put({"event_type": "tile_placed", "data": {
                "tile_id": data.get('tile_id'),
                "tile_type": data.get('tile_type')
            }})
    if 'city_location' in data:
        event_queue.put({"event_type": "city_changed", "data": {
            "city_id": data.get('city_location')
        }})
    if 'time' in data:
        event_queue.put({"event_type": "time_changed", "data": {
            "time": data.get('time')
        }})
