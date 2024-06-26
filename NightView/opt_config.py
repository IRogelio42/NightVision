replacement = {
    "Killer" : {
            "Survivors": {
                "2560x1440" : {
                    "0": {
                        "w": 347,
                        "h": 118,
                        "x" : 100,
                        "y" : 545,
                    },
                    "1": {
                        "w": 347,
                        "h": 118,
                        "x" : 100,
                        "y" : 663,
                    },
                    "2": {
                        "w": 347,
                        "h": 118,
                        "x" : 100,
                        "y" : 781,
                    },
                    "3": {
                        "w": 347,
                        "h": 118,
                        "x" : 100,
                        "y" : 899,
                    },
                }
            },
            "Hook_Stages" : {
                "2560x1440" : {
                    "x" : 207,
                    "y" : 40,
                    "w" : 27,
                    "h" : 38
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
                    "0": { # self
                        "w": 347,
                        "h": 118,
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
                "x" : 228,
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
            "Injured": {"Filename": "injured.png", "Threshold": .8, },
            "Down": {"Filename": "down.png", "Threshold": .8, },
            "Dead": {"Filename": "dead.png", "Threshold": .8, },
            "Mori": {"Filename": "mori.png", "Threshold": .8, },
            "Hook_Stage0": {"Filename": "HS0.png", "Threshold": .8, },
            "Hook_Stage1": {"Filename": "HS1.png", "Threshold": .8, },
            "Hook_Stage2": {"Filename": "HS2.png", "Threshold": .8, },
            #Need to decide how to track stages, whether hold all images as above
            #or hold single image and save previous image to identify transition as below
            "Killer_Hooks": {"Filename": "KHS.png", "Threshold": .8,},
            # Similar problem for generator detection
            "Generator_Count": {"Filename": "Generators.png", "Threshold": .8},
    }
}
    