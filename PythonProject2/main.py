from TileManager import TileManager
from Calculator import Calculator
from City import City
from Heatmap_Creator import Heatmap_Creator
from Info import subtile_amount, grid_size
from flask import Flask, json, request, jsonify
import threading
import requests

url_uhi = "http://192.168.1.3:5000/output/uhi"
url_wind = "http://192.168.1.3:5000/output/wind"
url_death = "http://192.168.1.3:5000/output/death"

app = Flask(__name__)

# Shared state between Flask routes and main loop
state = {
    "tile_id": None,
    "tile_type": None,
    "city_update": None,   # city_id or None
    "month_update": 1 # temperature value or None
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
    
@app.route('/input/month', methods=['POST'])
def receive_month():
    data = request.get_json()
    try:
        month = data.get('month')
        with state_lock:
            state["month_update"] = month
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

def main():
    tile_manager = TileManager()
    calculator = Calculator()
    city = City()
    heatmap = Heatmap_Creator()
    player_id = None

    temperature = 0

    while True:
        # Grab and clear any pending updates
        with state_lock:
            tile_id = state.pop("tile_id", None)
            tile_type = state.pop("tile_type", None)
            city_id = state.pop("city_update", None)
            month = state.pop("month_update", None)

        if month is not None:
            print("new month received")
            with open("PythonProject2/month_data.json", 'r') as jsonfile:
                month_data = json.load(jsonfile)
                temperature = month_data[str(month)]["temperature"]
                death = month_data[str(month)]["death"]

            # Update calculations and heatmap
            update_everything(tile_manager, city, temperature, calculator, heatmap)

        if city_id is not None:
            print("new city")
            city.update_city(city_id)

            # Update calculations and heatmap
            update_everything(tile_manager, city, temperature, calculator, heatmap)

        if tile_type is not None and tile_id is not None:
            print("new tile")

            if tile_id == player_id:  # If player got replaced
                player_id = None
                send_wind_uhi_death(url_wind, 0)
                send_wind_uhi_death(url_uhi, 0)

            if tile_type <= 7:  # if not a character
                tile_manager.update_tile(tile_id, tile_type)
            else:  # if character
                tile_type -= 7
                tile_manager.update_tile(tile_id, tile_type)
                player_id = tile_id # Update player position

            # Update calculations and heatmap
            update_everything(tile_manager, city, temperature, calculator, heatmap)

            # Only output if we know where the player is
            if player_id is not None:
                output = build_player_output(player_id, tile_manager, city, temperature, death)
                send_wind_uhi_death(url_wind, output["wind"])
                send_wind_uhi_death(url_uhi, output["uhi"])
                send_wind_uhi_death(url_death, output["death"])

                # SEND TO UNITY AS WELL
            else:
                send_wind_uhi_death(url_wind, 0)
                send_wind_uhi_death(url_uhi, 0)
                send_wind_uhi_death(url_death, 0)

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
    wind_data = city.wind

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

def send_wind_uhi_death(url, payload):
    try:
        resp = requests.post(url, json= payload, timeout=1)
    except Exception as e:
        print(f"error {e}")

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True)
    flask_thread.start()
    main()