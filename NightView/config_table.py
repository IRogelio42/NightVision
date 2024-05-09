from copy import deepcopy
import json
import os

aspect_ratios = {
    0 : {
        "id" : "16:9",
        "sample_w": 1920,
        "sample_h": 1080,
    },
    1: {
        "id" : "21:9",
        "sample_w": 2560,
        "sample_h": 1080,
    },
    2: {
        "id" : "16:10",
        "sample_w": 1680,
        "sample_h": 1050,
        "template_scaling": 1680/1920
    },
}

#4/23 Current Goal Add Locations of 1440p, then to figure out rest
config = {
    "monitor_number": 1,
    "aspect_ratio_index": 0,
    "show_overlay_mode": 0,
    "show_regions_mode": 0,
    "player" : 0,
    "regions": {
        "player_type": {
                "2560x1440" : {
                    "w" : 128,
                    "h" : 87,
                    "x" : 2348,
                    "y" : 1305
                },
            },
        "Temp" : 
            {},
        "Perks" : {
        # Left, Right, Down, Up
            "2560x1440" : {
                "w": 154,
                "h": 154,
                ""
                "0": {
                    "x" : 2137,
                    "y" : 1121,
                },
                "1": {
                    "x" : 2325,
                    "y" : 1121,
                },
                "2": {
                    "x" : 2231,
                    "y" : 1214,
                },
                "3": {
                    "x" : 2231,
                    "y" : 1028,
                },
            },
        }
    }
}

#4/30 Need To Write  Afuntion that upon detection of player rewrites config[regions] in order to streamline code

def save_to_file():
    save_dict = deepcopy(config)
    del save_dict["regions"]
    for det in save_dict["detectables"].values():
        for field in list(det.keys()):
            if (field not in ["points", "type"]):
                del det[field]

    with open('config.json', 'w') as f:
        json.dump(save_dict,  f, indent= 4)

def load_from_file():
    if os.path.exists('config.json'):
        print("Loading config file...")
        with open('config.json', 'r') as f:
            load_dict = json.load(f)
            for key in load_dict.keys():
                if key in ["detectables"]:
                    for detectable in load_dict[key].keys():
                        for field in load_dict[key][detectable].keys():
                            config[key][detectable][field] = load_dict[key][detectable][field]
                else:
                    config[key] = load_dict[key]