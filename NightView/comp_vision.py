import os
import time
import mss
import numpy as np
import cv2 as cv

from config_table import config, aspect_ratios


class ComputerVision():
    def __init__(self) -> None:
        self.last_update = 0
        self.min_update_period = 0.1
        self.detection_ping = 0

        self.debug_image = None
        self.detection_rect = {}
        self.resolution_scaling_factor = 1
        self.resolution_changed = False
        self.detect_resolution()

    def detect_resolution(self):
        scale = 1
        monitor_rect = {}
        with mss.mss() as sct:
            monitor_rect = sct.monitors[1]  # Use the 1st monitor

        if self.detection_rect == monitor_rect:
            return False
        else:
            print("Setting detection rect: " + str(monitor_rect))
            self.detection_rect = monitor_rect
            self.resolution_scaling_factor = scale
            # self.detectables_setup()
            return True

    def update(self):
        t0 = time.time()
        if t0 - self.last_update < self.min_update_period:
            return False
        delta_time = min(1, t0 - self.last_update)
        self.last_update = t0

        self.resolution_changed = self.detect_resolution()

        # for r in config["regions"]:
        #    config["regions"][r]["Matches"] = []
        # for d in config["detectables"]:
        #    config["detectables"][d]["Count"] = 0

        # self.update_detections()

        # frame_delta_points = 0
        # for d in config["detectables"]:
        #    if d == "KillcamOrPOTG":
        #        continue
        #    if config["detectables"][d]["type"] == 0:
        #        self.score_instant += config["detectables"][d]["Count"] * config["detectables"][d]["points"]
        #    elif config["detectables"][d]["type"] == 1:
        #        frame_delta_points += config["detectables"][d]["Count"] * config["detectables"][d]["points"]
        #    elif config["detectables"][d]["type"] == 2:
        #        frame_delta_points += config["detectables"][d]["Count"] * config["detectables"][d]["points"] / \
        #                              config["detectables"][d]["duration"]

        t1 = time.time()
        a = .1
        self.detection_ping = (1 - a) * self.detection_ping + a * (t1 - t0)
        return True

    def grab_current_frame(self):
        top = self.detection_rect["height"]
        left = self.detection_rect["width"]
        bottom = 0
        right = 0
        regionNames = config["regions"]

        for region in regionNames:
            if type(region) is list:
                rect = config["regions"][region]["2560x1440"]
                for i in range(0, 4):
                    top = min(top, rect[str(i)]["y"])
                    bottom = max(bottom, rect[str(i)]["y"] + rect["h"])
                    left = min(left, rect[str(i)]["x"])
                    right = max(right, rect[str(i)]["x"] + rect["w"])
            else:
                rect = config["regions"][region]["2560x1440"]
                top = min(top, rect["y"])
                bottom = max(bottom, rect["y"] + rect["h"])
                left = min(left, rect["x"])
                right = max(right, rect["x"] + rect["w"])

        self.frame_offset = (top, left)

        top += self.detection_rect["top"]
        bottom += self.detection_rect["top"]
        left += self.detection_rect["left"]
        right += self.detection_rect["left"]

        with mss.mss() as sct:
            region = (left, top, right, bottom)  # (config["regions"]["Survivors"]["2560x1440"]["0"]["x"],
            # config["regions"]["Survivors"]["2560x1440"]["0"]["y"],
            # config["regions"]["Survivors"]["2560x1440"]["0"]["x"]
            #  + config["regions"]["Survivors"]["2560x1440"]["w"],
            # config["regions"]["Survivors"]["2560x1440"]["0"]["y"]
            #  + config["regions"]["Survivors"]["2560x1440"]["h"])
            # self.frame = np.array(sct.grab(sct.monitors[1]))[:, :, :]
            try:
                self.frame = np.array(sct.grab(region))[:, :, :]
            except:
                print("Fucked Up!")

        return self.frame, region[2] - region[0], region[3] - region[1]