# Lookup lists
type_effect = {
    "built_low": 0,
    "built_high": 0,
    "trees": 0.5,
    "low_veg": 0.2,
    "water": 0.3,
    "farmland": 0.2,
    "built_low_char": 0,
    "built_high_char": 0,
    "apartment_char": 0,
    "canals_char": 0.3,
    "lakes_char": 0.3,
    "parks_char": 0.3,
    "forests_char": 0.5,
    "farmland_char": 0.2,
    "sea": 1
}

type_roughness = {
    "built_low": 1,
    "built_high": 2,
    "trees": 1,
    "low_veg": 0.1,
    "water": 0.005,
    "farmland": 0.25,
    "built_low_char": 1,
    "built_high_char": 2,
    "apartment_char": 2,
    "canals_char": 0.005,
    "lakes_char": 0.005,
    "parks_char": 0.5,
    "forests_char": 1,
    "farmland_char": 0.25,
    "sea": 0.005
}

types = ("built_low",
         "built_high",
         "trees",
         "low_veg",
         "water",
         "sea",
         "farmland",
         "built_low_char",
         "built_high_char",
         "apartment_char",
         "canals_char",
         "lakes_char",
         "parks_char",
         "forests_char",
         "farmland_char")

# Project parameters
grid_size = (8, 6)
subtile_amount = 9  # 2x2 within tile
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
url_output = "http://192.168.1.3:5000/output"
url_input = "http://192.168.1.1:5000/input"

# Settings
EVENT_DEBUG = True
OUTPUT_DEBUG = False
NEW_TILE_UHI_DEBUG = True
allow_fake_input = False
use_type_dots = True
