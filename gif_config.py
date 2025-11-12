import json
from dataclasses import asdict, dataclass
import os

@dataclass
class Config:
    RES_X: int = 1920
    RES_Y: int = 1080
    FPS: int = 30
    GIF_QUALITY: int = 50
    TAB: bool = True
    TAB_LENGTH: int = 2
    FONT_NAME: str = ""
    FONT_PATH: str = "FSEX302.ttf"
    FONT_SIZE: int = 30
    FONT_COLOR: tuple = (0, 255, 0)
    LINE_SPACE: int = 45
    DURATION_TEXT: int = 2
    DURATION_CURSOR: int = 2
    EFFECT_WARP_INTENSITY: float = 0.15
    EFFECT_SCANLINE_INTENSITY: float = 0.3
    EFFECT_NOISE_INTENSITY: float = 0.03
    EFFECT_GLOW_INTENSITY: int = 3
    OVERRIDE_LINUX: str = ""
    OVERRIDE_KERNEL: str = ""
    OVERRIDE_DE: str = ""
    OVERRIDE_BASH: str = ""
    OVERRIDE_PHYS_MEM: str = ""

    def print_config(self):
        for field in self.__dataclass_fields__:
            print(f"{field}: {getattr(self, field)}")

    def save_to_json(self, filename="config.json"):
        # Convert the dataclass instance to a dictionary
        config_dict = asdict(self)

        # Write the dictionary to a JSON file
        with open(filename, 'w') as json_file:
            json.dump(config_dict, json_file, indent=4)
        
        print(f"Config saved to {filename}")

    @classmethod
    def load_from_json(cls, filename="config.json"):
        if not os.path.exists(filename):
            print(f"{filename} does not exist. Creating a new configuration file with default values.")
            config_instance = cls()  # Create a new instance with default values
            config_instance.save_to_json(filename)  # Save the default config to a new JSON file
            return config_instance  # Return the default config instance
        
        # Load the dictionary from the JSON file
        with open(filename, 'r') as json_file:
            config_dict = json.load(json_file)
        
        # Convert the dictionary back to a dataclass instance
        return cls(**config_dict)
    