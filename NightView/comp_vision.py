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

        self.prompt_detectables = ["player_type"]
        self.filters = {}
        #for d in self.prompt_detectables:
            #self.filters[d] = self.prompt_filter
        
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

        # Following If is a default of 2560x1440, no rescaling/ refitting done 5/19
        if self.detection_rect == monitor_rect:
            return False
        else:
            print("Setting detection rect: " + str(monitor_rect))
            self.detection_rect = monitor_rect
            self.resolution_scaling_factor = scale
            # self.detectables_setup()
            return True

    def dectectables(self):
        for region in config["region"]:
            i = config["0"]
            resolution = str(aspect_ratios[i]["sample_w"]) + "x" + str(aspect_ratios[i]["sample_h"])
            rect = config["regions"][region].get(resolution)  # Get method built into that data type,

            config["regions"][region]["ScaledRect"] = self.scale_rect(rect)
            config["regions"][region]["Matches"] = []  # Pings a Match

            for item in config["detectables"]:
                self.load_and_scale_template(config["detectables"][item])  # Scale template image
                if item in self.filters:
                    config["detectables"][item]["template"] = self.filters[item](config["detectables"][item]["template"]) 

    def update(self):
        t0 = time.time()
        if t0 - self.last_update < self.min_update_period:
            return False
        delta_time = min(1, t0 - self.last_update)
        self.last_update = t0

        self.resolution_changed = self.detect_resolution()

        for r in config["regions"]:
           config["regions"][r]["Matches"] = []
        for d in config["detectables"]:
           config["detectables"][d]["Count"] = 0

        self.update_detections()

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

    def update_detections(self):
        self.match_detectables_on_region("Prompt", self.prompt_detectables)

        lower_regions = [r for r in config["regions"]]
        self.grab_frame_cropped_to_regions(lower_regions)

        # Hero Specific
        for item in ["Give Harmony Orb", "Give Discord Orb", "Give Mercy Boost", "Give Mercy Heal"]:
            self.match_detectables_on_region(item, [item])

        # Receive Heals
        healDetectables = ["Receive Zen Heal", "Receive Mercy Boost", "Receive Mercy Heal"]
        self.match_detectables_on_region("Receive Heal", healDetectables)

        # Status
        statusDetectables = ["Receive Hack", "Receive Discord Orb", "Receive Anti-Heal", "Receive Heal Boost", "Receive Immortality"]
        self.match_detectables_on_region("Receive Status Effect", statusDetectables)
    
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
            region = (left, top, right, bottom) 
            try:
                self.frame = np.array(sct.grab(region))[:, :, :]
            except:
                print("Fucked Up!")

        return self.frame, region[2] - region[0], region[3] - region[1]

    # Scale Detection Images to Appropriate Resolution necessary
    def load_and_scale_template(self, item):
        path = os.path.join(os.path.abspath("."), "templates", item["filename"])
        # cv.imread(path) -> returns image at path location as variable
        base_template = cv.imread(path)

        template_scaling = aspect_ratios[config["aspect_ratio_index"]].get("template_scaling", 1)
        height = int(base_template.shape[0] * self.resolution_scaling_factor * template_scaling)
        width = int(base_template.shape[1] * self.resolution_scaling_factor * template_scaling)
        # resize (image, (w, h))
        scaled = cv.resize(base_template.copy(), (width, height))

        item["original_image"] = base_template
        item["template"] = scaled