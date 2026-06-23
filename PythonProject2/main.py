import pygame

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
import json
import socket
import viewheatmap

url_output = "http://192.168.1.3:5000/output"
url_input = "http://192.168.1.1:5000/input"
allow_fake_input = True

app = Flask(__name__)

# Shared state between Flask routes and main loop
state = {
    "tile_id": None,
    "tile_type_id": None,
    "city_update": 0, # start in Eindhoven
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

    print(data)

    if 'tile_id' in data and 'tile_type_id' in data:
        tile_id = data.get('tile_id')
        tile_type = data.get('tile_type_id')
        with state_lock:
            state["tile_type_id"] = tile_type
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
    game = viewheatmap.GameDisplay(1600, 900, "heatmap.png", display_index=1)
    clock = pygame.time.Clock()
    temperature = 0
    death = 0

    update_done = threading.Event()  # add here

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if allow_fake_input: detect_fake_input()

        with state_lock:
            tile_id = state.pop("tile_id", None)
            tile_type_id = state.pop("tile_type_id", None)
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

        if tile_type_id is not None and tile_id is not None:
            print(f"new tile received: {tile_id}, type: {tile_type_id}")

            if tile_id == player_id:
                player_id = None
                build_player_output(player_id, tile_manager, city, temperature, death)
                send_output(output)
                print("Output: 0, 0, 0")

            if tile_type_id <= 6:
                tile_manager.update_tile(tile_id, tile_type_id)
            else:
                tile_manager.update_tile(tile_id, tile_type_id)
                player_id = tile_id

        if tile_type_id is not None or tile_id is not None or month is not None or city_id is not None:
            update_done.clear()
            threading.Thread(target=lambda: [update_everything(tile_manager, city, calculator, heatmap), update_done.set()], daemon=True).start()

            if player_id is not None:
                output = build_player_output(player_id, tile_manager, city, temperature, death)
                send_output(output)
                print(f"output: {output['wind']}, {output['uhi']}, {output['death']}")
            else:
                output = build_player_output(player_id, tile_manager, city, temperature, death)
                send_output(output)
                print(f"output: {output['wind']}, {output['uhi']}, {output['death']}")

        # update display only when heatmap file is freshly written
        if update_done.is_set():
            game.update()
            update_done.clear()

        clock.tick(60)


def update_everything(tile_manager, city, calculator, heatmap):
    # Update calculations and heatmap
    all_subtiles = tile_manager.get_subtiles()
    calculator.update_calculation(city, all_subtiles, tile_manager.get_soil_population()[1], tile_manager.get_soil_population()[0])
    heatmap.update_heatmap(all_subtiles)


# Collect all player output data and return
def build_player_output(player_id, tile_manager, city, temperature, death):
    if player_id is None:
        return {
            "uhi": 0,
            "wind": 0,
            "land_use": 0,
            "death": 0,
            "city": None,
            "neighbors": {
                "front": None,
                "left": None,
                "right": None
            }
        }
    
    x = int(player_id % grid_size[0])
    y = int(player_id // grid_size[1])


    wind, uhi, death_to_UHI = get_player_loc_data((x, y), city, tile_manager, temperature, death)

    tile = tile_manager.tiles[x, y]

    def get_neighbor_type(nx, ny):
        if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
            return tile_manager.tiles[nx, ny].type
        else:
            return city.fake_tiles[nx + 1, ny + 1]

    # Population of straight neighbours
    population = tile.population + tile_manager.tiles[x + 1, y].population + tile_manager.tiles[x - 1, y].population + tile_manager.tiles[x, y + 1].population + tile_manager.tiles[x, y - 1].population


    # neighbors: for connect with scene in Unity
    return{
        "uhi": uhi,
        "wind": wind,
        "land_use": tile.type,
        "death": death_to_UHI,
        "city": city.name,
        "population": int(population / 45),
        "neighbors":{
            "front": get_neighbor_type(x-1, y),
            "left": get_neighbor_type(x, y-1),
            "right": get_neighbor_type(x, y+1),
        }
    }

def send_state(state: dict):
    msg = json.dumps(state).encode()
    sock.sendto(msg, (UDP_IP, UDP_PORT))

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

def send_output(output):
    try:
        resp = requests.post(url_input, json=output, timeout=1)
    except Exception as e:
        print(f"error {e}")
    try:
        send_state(output)
    except Exception as e:
        print("unity error")
        print(f"error {e}")

def detect_fake_input():
    if random.randint(0, 1000000) == 1:
        with state_lock:
            state["tile_type"] = random.randint(0, 6) # Random tile type
            state["tile_id"] = random.randint(0, 47) # Random location
    if random.randint(0, 1000000) == 1:
        with state_lock:
            state["city_update"] = random.randint(0, 9) # Random city
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