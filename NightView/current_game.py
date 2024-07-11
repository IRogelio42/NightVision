import os

class Game():
    def __init__(self, p_type):
        self.player = p_type
        self.game = {
            "Killer" : "",
            "Survivor_1" : {"Name" : "", "Hits" : 0, "CurrentHS" : 0, "Character" : "", "Health" : ""},
            "Gens" : 5,
            "Win" : ""
        }
        
        if lower(self.player) is "killer":
            self.game["Hooks"] = 0
            self.game["Survivor_1"].pop("CurrentHS")
            for i in range(2, 4):
                self.game["Survivor_" + i] = self.game["Survivor_1"]
        elif lower(self.player) is "survivor":
            self.game["Hooked"] = 0
            self.game["Survivor_1_Self"] = self.game.pop("Survivor_1")

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
