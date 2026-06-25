from TileManager import TileManager
from Calculator import Calculator
from City import City
from flask import Flask, json, request, jsonify
import threading
import requests
from pathlib import Path
import random
import json
import socket
from BeamerAssembler import Heatmap
from BorderImages import Borders
import numpy as np
from Output import build_player_output

url_output = "http://192.168.1.3:5000/output"
url_input = "http://192.168.1.1:5000/input"
allow_fake_input = False

app = Flask(__name__)

# Shared state between Flask routes and main loop
state = {
    "tile_id": None,
    "tile_type_id": None,
    "city_update": 1, # start in Den Helder
    "month_update": 1 # start in January
}
state_lock = threading.Lock()

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Receive data
@app.route('/input', methods=['GET', 'POST'])
def receive_data():

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Expected JSON object"}), 400

    # print(data)

    if 'tile_id' in data and 'tile_type' in data:
        tile_id = data.get('tile_id')
        tile_type_id = data.get('tile_type')
        with state_lock:
            state["tile_type_id"] = tile_type_id
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
    heatmap = Heatmap(3, True)
    borders = Borders(heatmap.size)


    player_id = None
    temperature = 0
    death = 0

    while True:

        if allow_fake_input: create_fake_input()

        with state_lock:
            tile_id = state.pop("tile_id", None)
            tile_type_id = state.pop("tile_type_id", None)
            city_id = state.pop("city_update", None)
            month = state.pop("month_update", None)

        if month is not None: # If new month
            print(f"new month received: {month}")
            with open(Path(__file__).parent / "month_data.json", 'r') as jsonfile:
                month_data = json.load(jsonfile)
                temperature = month_data[str(month)]["temperature"]
                death = month_data[str(month)]["death"]

        if city_id is not None: # If new city
            city.update_city(city_id)
            heatmap.update_border(borders.get_border(city.name))

            print(f"new city received: {city_id}, {city.name}")

        if tile_type_id is not None and tile_id is not None: # If new tile

            if tile_id == player_id: # If player got replaced with tile
                player_id = None
                build_player_output(player_id, tile_manager, city, temperature, death)
                send_output(output)

                heatmap.clear_spotlight() # Clear spotlight if player got replaced with tile

            if tile_type_id <= 6: # If not player
                tile_manager.update_tile(tile_id, tile_type_id)
            else: # If player
                tile_manager.update_tile(tile_id, tile_type_id)
                player_id = tile_id

                heatmap.set_spotlight(player_id) # Update spotlight if player got added

        if tile_type_id is not None or tile_id is not None or month is not None or city_id is not None:

            update_everything(tile_manager, city, calculator, heatmap)

            if player_id is not None:
                output = build_player_output(player_id, tile_manager, city, temperature, death)
                send_output(output)
            else:
                output = build_player_output(player_id, tile_manager, city, temperature, death)
                send_output(output)


def update_everything(tile_manager, city, calculator, heatmap):
    # Update calculations and heatmap
    all_subtiles = tile_manager.get_subtiles()
    calculator.update_calculation(city, all_subtiles, tile_manager.get_soil_population()[1], tile_manager.get_soil_population()[0])
    get_UHI = np.vectorize(lambda subtile: subtile.UHI)
    UHI_array = get_UHI(all_subtiles)
    heatmap.update_grid(UHI_array)

    # Display tile types
    get_type = np.vectorize(lambda tile: tile.type_id)
    type_array = get_type(tile_manager.tiles)
    heatmap.update_grid_ids(type_array)

def send_state(state: dict):
    msg = json.dumps(state).encode()
    print(msg)
    sock.sendto(msg, (UDP_IP, UDP_PORT))

def send_output(output):
    try:
        resp = requests.post(url_output, json=output, timeout=1)
    except Exception as e:
        print(f"error {e}")
        pass
    try:
        send_state(output)
    except Exception as e:
        print("unity error")
        print(f"error {e}")

def create_fake_input():
    if random.randint(0, 1000000) == 1:
        with state_lock:
            state["tile_type"] = random.randint(0, 6) # Random tile type
            state["tile_id"] = random.randint(0, 47) # Random location
    # if random.randint(0, 1000000) == 1:
    #     with state_lock:
    #         state["city_update"] = random.randint(0, 9) # Random city
    # if random.randint(0, 1000000) == 1:
    #     with state_lock:
    #         state["month_update"] = random.randint(1, 12) # Random month
    if random.randint(0, 2000000) == 1:
        with state_lock:
            state["tile_type"] = random.randint(7, 14) # Random character tile
            state["tile_id"] = random.randint(0, 47) # Random location

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True)
    flask_thread.start()
    main()