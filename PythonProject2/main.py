from TileManager import TileManager
from Calculator import Calculator
from City import City
from Heatmap_Creator import Heatmap_Creator
from Info import subtile_amount, grid_size
from flask import Flask, request, jsonify
import threading
import requests

url_uhi = "https://192.168.1.3:5000/output/uhi"
url_wind = "https://192.168.1.3:5000/output/wind"

app = Flask(__name__)

# Shared state between Flask routes and main loop
state = {
    "tile_id": None,
    "tile_type": None,
    "city_update": None   # city_name or None
}
state_lock = threading.Lock()


@app.route('/input/tile_information', methods=['POST'])
def receive_tile_data():
    data = request.get_json()
    print(data)
    try:
        tile_id = data.get('tile_id')
        tile_type = data.get('tile_type')
        with state_lock:
            state["tile_type"] = tile_type
            state["tile_id"] = tile_id
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/input/city_location', methods=['POST'])
def receive_city_name():
    data = request.get_json()
    try:
        city_name = data.get('city_location')
        with state_lock:
            state["city_update"] = city_name
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

def main():
    tile_manager = TileManager()
    calculator = Calculator()
    city = City()
    heatmap = Heatmap_Creator()
    player_grid_pos = None # Tuple, but None when no player placed

    while True:
        # Grab and clear any pending updates
        with state_lock:
            tile_id = state.pop("tile_id", None)
            tile_type = state.pop("tile_type", None)
            city_name = state.pop("city_update", None)

        if city_name is not None:
            print("new city")
            city = city.update_city(city_name)

        if tile_type is not None and tile_id is not None:
            print("new tile")

            if tile_id == player_grid_pos:  # If player got replaced
                player_grid_pos = None
                send_wind_uhi(url_wind, 0)
                send_wind_uhi(url_uhi, 0)

            if tile_type <= 7:  # if not a character
                tile_manager.update_tile(tile_id, tile_type)
            else:  # if character
                tile_type -= 7
                tile_manager.update_tile(tile_id, tile_type)
                player_grid_pos = tile_id # Update player position

            # Update calculations and heatmap
            all_subtiles = tile_manager.get_subtiles()
            calculator.update_calculation(city, all_subtiles)
            heatmap.update_heatmap(all_subtiles)

            # Only output if we know where the player is
            if player_grid_pos is not None:
                output = build_player_output(player_grid_pos, tile_manager, city)
                send_wind_uhi(url_wind, output["wind"])
                send_wind_uhi(url_uhi, output["uhi"])
            else:
                send_wind_uhi(url_wind, 0)
                send_wind_uhi(url_uhi, 0)


def get_player_loc_data(player_pos, city, tile_manager):
    # Get UHI and wind data at player location
    wind_data = city.wind

    total_wind = 0

    tile = tile_manager.tiles[player_pos % grid_size[0], player_pos // grid_size[1]] # Tile of player
    total_UHI = 0
    for subtile in tile.subtiles.flat: # For each subtile within the player's tile
        total_UHI += subtile.UHI # Get subtile UHI
        total_wind += wind_data[subtile.total_subtile_pos] # Get subtile wind

    # Final data to output
    average_UHI = total_UHI / subtile_amount
    average_wind = total_wind / subtile_amount

    return average_wind, average_UHI


# Collect all player output data and return
def build_player_output(player_pos, tile_manager, city):
    uhi, wind = get_player_loc_data(player_pos, city, tile_manager)

    x = int(player_pos % grid_size[0])
    y = int(player_pos // grid_size[1])

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
        "neighbors":{
            "front": get_neighbor_type(x-1, y),
            "left": get_neighbor_type(x, y-1),
            "right": get_neighbor_type(x, y+1),
        }
    }

def send_wind_uhi(url, payload):
    try:
        resp = requests.post(url, json= payload, timeout=1)
    except Exception as e:
        print(f"error {e}")

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True)
    flask_thread.start()
    main()