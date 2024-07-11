from copy import deepcopy
import json
import os

aspect_ratios = {
    0 : {
        "id" : "16:9",
        "sample_w": 2560,
        "sample_h": 1440,
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
    },
    "detectables": {
        # similar to regions, replace upon state change, save rest on txt file
        # need to identify manners of detection
        "player_type" : {
            "player_typeA": {"filename": "player_typeA.png", "threshold": .76},
            "player_typeB": {"filename": "player_typeB.png", "threshold": .76},
        },
    }
}

replacement = {
    "Killer" : {
            "Survivors": {
                "2560x1440" : {
                    "w": 143,
                    "h": 118,
                    "0": {
                        "x" : 100,
                        "y" : 545,

                    },
                    "1": {
                        "x" : 100,
                        "y" : 663,
                    },
                    "2": {
                        "x" : 100,
                        "y" : 781,
                    },
                    "3": {
                        "x" : 100,
                        "y" : 899,
                    },
                }
            },
            "Hook_Stages" : {
                "2560x1440" : {
                    "x" : 129,
                    "y" : 1063,
                    "w" : 80,
                    "h" : 80
                    }
            },
            "Generators" : {
                "2560x1440" : {
                    "w": 136,
                    "h": 94,
                    "x" : 228,
                    "y" : 1058,
                },
            },
        },
    "Survivor" : {
            "Survivors": {
                "2560x1440": {
                    "w": 143,
                    "h": 118,
                    "0": { # self
                        "x": 100,
                        "y": 545,
                    },
                },
            },
            "Hook_Stages": {
                "2560x1440": {
                    "x": 307,
                    "y": 585,
                    "w": 27,
                    "h": 38
                }
            },
        "Survivor_Actions": {
            "2560x1440": {
                "x": 244,
                "y": 572,
                "w": 50,
                "h": 50
            }
        },
        "Generators" : {
            "2560x1440" : {
                "w": 136,
                "h": 94,
                "x" : 132,
                "y" : 1058,
            },
        }
    },
    "Perks" : {
            # Left, Right, Down, Up
                "2560x1440" : {
                    "w": 154,
                    "h": 154,
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
                    }
                },
    },
    "detectable" : {
            # Survivor detectables apply to both,
            "Survivor" : {
                "Injured": {"Filename": "injured.png", "Threshold": .8, },
                "Down": {"Filename": "down.png", "Threshold": .8, },
                "Dead": {"Filename": "dead.png", "Threshold": .8, },
                "Mori": {"Filename": "mori.png", "Threshold": .8, },
                "Hook_Stage0": {"Filename": "HS0.png", "Threshold": .8, },
                "Hook_Stage1": {"Filename": "HS1.png", "Threshold": .8, },
                "Hook_Stage2": {"Filename": "HS2.png", "Threshold": .8, },
            },
            #Need to decide how to track stages, whether hold all images as above
            #or hold single image and save previous image to identify transition as below
            "Killer" : {
                #Since neither of these regress, update filename to next state
                #ie KHS1-12(?) and Gens5-0
                "Killer_Hooks": {"Filename": "KHS1.png", "Threshold": .8,},
                # Similar problem for generator detection
                "Generator_Count": {"Filename": "5gen.png", "Threshold": .8},
            },

    }
}
#4/30 Need To Write  Afuntion that upon detection of player rewrites config[regions] in order to streamline code

def exchange_from_file(player_type="player_type"):
    global replacement
    config["player"] = 1 if player_type == "Survivor" else 2
    save_dict = deepcopy(config)
    temp = config["regions"]
    config["regions"] = replacement[player_type]
    config["regions"]["Perks"] = replacement["Perks"]
    replacement = temp
    #for det in save_dict["detectables"].values():
    #    for field in list(det.keys()):
    #        if (field not in ["points", "type"]):
    #            del det[field]

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