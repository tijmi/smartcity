from TileManager import TileManager
from Calculator import Calculator
from City import City
from Heatmap_Creator import Heatmap_Creator
from Info import subtile_amount, grid_size
from flask import Flask, json, request, jsonify
import threading
import requests
from pathlib import Path
import random

url_uhi = "http://192.168.1.3:5000/output/uhi"
url_wind = "http://192.168.1.3:5000/output/wind"
url_death = "http://192.168.1.3:5000/output/death"
allow_fake_input = True

app = Flask(__name__)

# Shared state between Flask routes and main loop
state = {
    "tile_id": None,
    "tile_type": None,
    "city_update": 0, # start in Eindhoven
    "month_update": 1 # start in January
}
state_lock = threading.Lock()

# Receive data
@app.route('/input', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Expected JSON object"}), 400

    print(data)

    if 'tile_id' in data and 'tile_type' in data:
        tile_id = data.get('tile_id')
        tile_type = data.get('tile_type')
        with state_lock:
            state["tile_type"] = tile_type
            state["tile_id"] = tile_id
        return jsonify({"status": "ok"})

    if 'city_location' in data:
        city_id = data.get('city_location')
        with state_lock:
            state["city_update"] = city_id
        return jsonify({"status": "ok"})

    if 'month' in data:
        month = data.get('month')
        with state_lock:
            state["month_update"] = month
        return jsonify({"status": "ok"})

    return jsonify({"status": "error", "message": "Unknown payload shape"}), 400

def main():
    tile_manager = TileManager()
    calculator = Calculator()
    city = City()
    heatmap = Heatmap_Creator()
    player_id = None

    temperature = 0

    while True:

        if allow_fake_input: detect_fake_input() # Check for manual fake input

        # Grab and clear any pending updates
        with state_lock:
            tile_id = state.pop("tile_id", None)
            tile_type = state.pop("tile_type", None)
            city_id = state.pop("city_update", None)
            month = state.pop("month_update", None)

        if month is not None:
            print(f"new month received: {month}")
            with open(Path(__file__).parent / "month_data.json", 'r') as jsonfile:
                month_data = json.load(jsonfile)
                temperature = month_data[str(month)]["temperature"]
                death = month_data[str(month)]["death"]

        if city_id is not None:
            print(f"new city received: {city_id}")
            city.update_city(city_id)

        if tile_type is not None and tile_id is not None:
            print(f"new tile received: {tile_id}, type: {tile_type}")

            if tile_id == player_id:  # If player got replaced
                player_id = None
                send_wind_uhi_death(0, 0, 0)

                print("Output: 0, 0, 0")

            if tile_type <= 6:  # if not a character
                tile_manager.update_tile(tile_id, tile_type)
            else:  # if character
                tile_manager.update_tile(tile_id, tile_type)
                player_id = tile_id # Update player position

        # Update Calculations, Heatmap and Player data if update was received
        if tile_type is not None or tile_id is not None or month is not None or city_id is not None:
            update_everything(tile_manager, city, temperature, calculator, heatmap) # Update calculations and heatmap

            # Only output if we know where the player is
            if player_id is not None:
                output = build_player_output(player_id, tile_manager, city, temperature, death)
                send_wind_uhi_death(output["wind"], output["uhi"], output["death"])
                print(f"output: {output['wind']}, {output['uhi']}, {output['death']}")

                # SEND TO UNITY AS WELL
            else:
                output = build_player_output(0, tile_manager, city, temperature, death)
                send_wind_uhi_death(output["wind"], output["uhi"], output["death"])
                print(f"output: {output['wind']}, {output['uhi']}, {output['death']}")

def update_everything(tile_manager, city, temperature, calculator, heatmap):
    # Update calculations and heatmap
    all_subtiles = tile_manager.get_subtiles()
    calculator.update_calculation(city, all_subtiles, tile_manager.get_soil_population()[1], tile_manager.get_soil_population()[0], temperature)
    heatmap.update_heatmap(all_subtiles)


# Collect all player output data and return
def build_player_output(player_id, tile_manager, city, temperature, death):
    x = int(player_id % grid_size[0])
    y = int(player_id // grid_size[1])


    wind, uhi, death_to_UHI = get_player_loc_data((x, y), city, tile_manager, temperature, death)

    tile = tile_manager.tiles[x, y]

    def get_neighbor_type(nx, ny):
        if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
            return tile_manager.tiles[nx, ny].type
        return None

    # neighbors: for connect with scene in Unity
    return{
        "uhi": uhi,
        "wind": wind,
        "land_use": tile.type,
        "death": death_to_UHI,
        "neighbors":{
            "front": get_neighbor_type(x-1, y),
            "left": get_neighbor_type(x, y-1),
            "right": get_neighbor_type(x, y+1),
        }
    }

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

def send_wind_uhi_death(wind, uhi, death):
    try:
        resp = requests.post(url_uhi, json= uhi, timeout=1)
        resp = requests.post(url_wind, json= wind, timeout=1)
        resp = requests.post(url_death, json= death, timeout=1)
    except Exception as e:
        print(f"error {e}")

def detect_fake_input():
    if random.randint(0, 1000000) == 1:
        with state_lock:
            state["tile_type"] = random.randint(0, 6) # Random tile type
            state["tile_id"] = random.randint(0, 47) # Random location
    if random.randint(0, 1000000) == 1:
        with state_lock:
            state["city_update"] = random.randint(0, 4) # Random city
    if random.randint(0, 1000000) == 1:
        with state_lock:
            state["month_update"] = random.randint(1, 12) # Random month
    if random.randint(0, 2000000) == 1:
        with state_lock:
            state["tile_type"] = random.randint(7, 14) # Random character tile
            state["tile_id"] = random.randint(0, 47) # Random location

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True)
    flask_thread.start()
    main()