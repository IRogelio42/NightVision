import os

class Game():
    def __init__(self, p_type):
        self.player = p_type
        self.game = {
            "Killer" : "",
            "Survivor_1" : {"Name" : "",},
            "Survivor_2" : {"Name" : "",},
            "Survivor_3" : {"Name" : "",},
            "Survivor_4" : {"Name" : "",},
            "Gens" : 0,
            "Win" : ""
        }
        
        if lower(self.player) is "killer":
            self.game["Hooks"] = 0
            for i in range(1, 4):
                self.game["Survivor_" + i] = {}
                self.game["Survivor_" + i]["Name"] = ""
                self.game["Survivor_" + i]["Hits"] = 0
        else:
            self.game["Hooked"] = 0

    def game_finish(self):
        # Game winning logic
        # Need to check different conds based on self.player

        self.save_to_file()


    def save_to_file(self):
        # Need to write file checker to add appropriate enumeration
        game = self.player + "-" + self.game["Killer"] + "_" + ".txt"
        file = open(game, "a")

        #write class to file
        self.clear() # Destructor placeholder
