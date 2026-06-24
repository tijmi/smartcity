import imageio.v2 as iio
from PIL import Image
import numpy as np


class Borders:
    def __init__(self, display_size):
        w, h = display_size
        self.border_dict = {
            "Amsterdam": {"day": BorderImage("Amsterdam_Day.png", w, h), "night": BorderImage("Amsterdam_Night.png", w, h)},
            # "Scheveningen": {"day": BorderImage("Scheveningen_Day.png", w, h), "night": BorderImage("Scheveningen_Night.png", w, h)},
            # "Middelburg": {"day": BorderImage("Middelburg_Day.png", w, h), "night": BorderImage("Middelburg_Night.png", w, h)},
            # "Eindhoven": {"day": BorderImage("Eindhoven_Day.png", w, h), "night": BorderImage("Eindhoven_Night.png", w, h)},
            # "Klimmen": {"day": BorderImage("Klimmen_Day.png", w, h), "night": BorderImage("Klimmen_Night.png", w, h)},
            # "Kootwijk": {"day": BorderImage("Kootwijk_Day.png", w, h), "night": BorderImage("Kootwijk_Night.png", w, h)},
            # "Hengelo": {"day": BorderImage("Hengelo_Day.png", w, h), "night": BorderImage("Hengelo_Night.png", w, h)},
            # "Groningen": {"day": BorderImage("Groningen_Day.png", w, h), "night": BorderImage("Groningen_Night.png", w, h)},
            # "Kampen": {"day": BorderImage("Kampen_Day.png", w, h), "night": BorderImage("Kampen_Night.png", w, h)},
            # "Den_Helder": {"day": BorderImage("Den_Helder_Day.png", w, h), "night": BorderImage("Den_Helder_Night.png", w, h)},
             }

    def get_border(self, city_name):
        return self.border_dict[city_name]


class BorderImage:
    def __init__(self, path, resize_w, resize_h):
        img = iio.imread(path)
        self.data = np.array(
            Image.fromarray(img).resize((resize_w, resize_h), Image.LANCZOS)
        )
