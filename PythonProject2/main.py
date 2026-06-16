from dask.array import average

from TileManager import TileManager
from Calculator import Calculator
from City import City
from Info import subtile_amount
from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route('/input/tile_information', methods=['POST'])
def receive_tile_data():
    # Handle JSON data
    data = request.get_json()
    print(data)

    try:
        tile_pos = data.get('tile_id')
        tile_type = data.get('tile_location')
        return tile_pos, tile_type
    except:
        return -1, -1

@app.route('/input/city_location', methods=['POST'])
def receive_city_name():
    # Handle JSON data
    data = request.get_json()

    try:
        city_name = data.get('city_location')
        return city_name
    except:
        return -1

def main():
    tile_manager = TileManager()
    calculator = Calculator()
    city = City()
    player_grid_pos = None # Tuple, but None when no player placed

    player_UHI = 0
    player_wind = 0


    while True:

        # Get tile and city update (None if no update this frame)
        update_pos, update_type = receive_tile_data()
        city_name = receive_city_name()

        if city_name != -1:
            city = city.update_city(city_name)

            print("new city")

        if update_type != -1 and update_pos != -1:

            print("new tile")

            if update_pos == player_grid_pos:
                player_grid_pos = None

                player_UHI = 0
                player_wind = 0

            if update_type <= 8: # if not a character
                tile_manager.update_tile(update_pos, update_type)
            else: # if character
                update_type -= 8
                tile_manager.update_tile(update_pos, update_type)
                player_grid_pos = update_pos

                player_UHI, player_wind = get_player_loc_data(player_grid_pos, city, tile_manager)

            calculator.update_calculation(city, tile_manager.get_subtiles())

            # SEND OVER PLAYER RELATED DATA AS OUTPUT

def get_player_loc_data(player_pos, city, tile_manager):
    # Get UHI and wind data at player location
    wind_data = city.wind

    total_wind = 0

    tile = tile_manager.tiles[player_pos[0], player_pos[1]] # Tile of player
    total_UHI = 0
    for subtile in tile.subtiles.flat: # For each subtile within the player's tile
        total_UHI += subtile.UHI # Get subtile UHI
        total_wind += wind_data[subtile.total_subtile_pos] # Get subtile wind

    # Final data to output
    average_UHI = total_UHI / subtile_amount
    average_wind = total_wind / subtile_amount

    return average_wind, average_UHI


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    main()