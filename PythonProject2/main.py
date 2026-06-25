from dataclasses import dataclass
from flask import Flask
import threading
from pathlib import Path
from queue import Queue
import socket
from TileManager import TileManager
from Calculator import Calculator
from City import City
from BeamerAssembler import Heatmap
from BorderImages import Borders
from WebServer import start_flask
from Helper_Functions import create_fake_input
from SendOutput import ServerOutput
import Info
from PlayerLocation import PlayerLocation
from EventHandlers import handle_tile_placed, handle_tile_removed, handle_city_changed, handle_time_changed
from Debugger import debug

event_queue = Queue()
app = Flask(__name__)
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

@dataclass
class AppContext:
    tile_manager: TileManager
    calculator: Calculator
    city: City
    heatmap: Heatmap
    borders: Borders
    server_out: ServerOutput
    player: PlayerLocation


def main_thread(queue):

    while True:
        item = queue.get()  # sleeps here until something arrives
        event_type = item.get("event_type")

        match event_type:
            case "tile_placed":
                handle_tile_placed(context, item)
            case "tile_removed":
                handle_tile_removed(context, item)
            case "city_changed":
                handle_city_changed(context, item)
            case "time_changed":
                handle_time_changed(context, item)


if __name__ == '__main__':
    tile_manager = TileManager()
    calculator = Calculator()
    city = City(1)
    heatmap = Heatmap(3, True)
    borders = Borders(heatmap.size)
    server_out = ServerOutput(socket, Info)
    player = PlayerLocation()

    debug("Created instances", "PROGRAM_STARTUP")

    context = AppContext(tile_manager, calculator, city, heatmap, borders, server_out, player)

    start_flask(app, event_queue)
    debug("Started the webserver", "PROGRAM_STARTUP")
    if Info.allow_fake_input:
        fake_thread = threading.Thread(target=create_fake_input, args=(event_queue,), daemon=True)
        fake_thread.start()
    main_thread(event_queue)
