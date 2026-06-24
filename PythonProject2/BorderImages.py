import imageio.v2 as iio
from PIL import Image
import numpy as np
from pathlib import Path


class Borders:
    def __init__(self, display_size):
        w, h = display_size
        self.border_dict = {
            "Amsterdam": {"day": BorderImage(Path(__file__).parent / "Border_Images/Amsterdam_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Amsterdam_Night.png", w, h)},
            # "Scheveningen": {"day": BorderImage(Path(__file__).parent / "Border_Images/Scheveningen_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Scheveningen_Night.png", w, h)},
            # "Middelburg": {"day": BorderImage(Path(__file__).parent / "Border_Images/Middelburg_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Middelburg_Night.png", w, h)},
            # "Eindhoven": {"day": BorderImage(Path(__file__).parent / "Border_Images/Eindhoven_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Eindhoven_Night.png", w, h)},
            # "Klimmen": {"day": BorderImage(Path(__file__).parent / "Border_Images/Klimmen_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Klimmen_Night.png", w, h)},
            # "Kootwijk": {"day": BorderImage(Path(__file__).parent / "Border_Images/Kootwijk_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Kootwijk_Night.png", w, h)},
            # "Hengelo": {"day": BorderImage(Path(__file__).parent / "Border_Images/Hengelo_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Hengelo_Night.png", w, h)},
            # "Groningen": {"day": BorderImage(Path(__file__).parent / "Border_Images/Groningen_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Groningen_Night.png", w, h)},
            # "Kampen": {"day": BorderImage(Path(__file__).parent / "Border_Images/Kampen_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Kampen_Night.png", w, h)},
            # "Den_Helder": {"day": BorderImage(Path(__file__).parent / "Border_Images/Den_Helder_Day.png", w, h), "night": BorderImage(Path(__file__).parent / "Border_Images/Den_Helder_Night.png", w, h)},
             }

    def get_border(self, city_name):
        return self.border_dict[city_name]


class BorderImage:
    def __init__(self, path, resize_w, resize_h):
        img = iio.imread(path)
        self.data = np.array(
            Image.fromarray(img).resize((resize_w, resize_h), Image.LANCZOS)
        )
