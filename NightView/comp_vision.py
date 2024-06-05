import os
import time
import mss
import numpy as np
import cv2 as cv

from config_table import config, aspect_ratios, exchange_from_file


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
        self.regions_changed = False
        self.detect_resolution()

    def detect_resolution(self):
        scale = 1
        monitor_rect = {}
        with mss.mss() as sct:
            monitor_rect = sct.monitors[2]  # Use the 1st monitor

        # Following If is a default of 2560x1440, no rescaling/ refitting done 5/19
        if self.detection_rect == monitor_rect:
            return False
        else:
            print("Setting detection rect: " + str(monitor_rect))
            self.detection_rect = monitor_rect
            self.resolution_scaling_factor = scale
            self.dectectables()
            return True

    def dectectables(self):
        for region in config["regions"]:
            i = 0
            resolution = str(aspect_ratios[i]["sample_w"]) + "x" + str(aspect_ratios[i]["sample_h"])
            rect = config["regions"][region].get(resolution)  # Get method built into that data type,

            config["regions"][region]["ScaledRect"] = self.scale_rect(rect)
            config["regions"][region]["Matches"] = []  # Pings a Match

            for item in config["detectables"][region]:
                self.load_and_scale_template(config["detectables"][region][item])  # Scale template image
                if item in self.filters:
                    config["detectables"][region][item]["template"] = self.filters[item](config["detectables"][region][item]["template"])

    def update(self):
        t0 = time.time()
        if t0 - self.last_update < self.min_update_period:
            return False
        delta_time = min(1, t0 - self.last_update)
        self.last_update = t0

        self.resolution_changed = self.detect_resolution()

        if len(config["regions"]) == 1: #temp override
            for r in config["regions"]:
               config["regions"][r]["Matches"] = []
               for d in config["detectables"][r]:
                   config["detectables"][r][d]["Count"] = 0

        self.update_detections()

        if len(config["regions"]) == 1:
            for d in config["detectables"][r]:
                if config["detectables"][r][d]["Count"]:
                    if config["regions"][r]["Matches"][0] == "player_typeA":
                        var="Survivor"
                    else:
                        var="Killer"
                    exchange_from_file(var)
                    print(var + " identified.")
                    self.regions_changed = True

        #for r in config["regions"]:
        #    for d in config["detectables"][r]:
        #        if config["detectables"][r][d]["Count"]:

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
        #match_detectables_on_region(regiontype, detectableKeys(what to look for))

        regions = [r for r in config["regions"]]
        self.grab_AOI(regions)

        if "player_type" == regions[0] and len(regions) == 1: # State 0
            self.match_detectables_on_region(regions[0], config["detectables"][regions[0]])
            return
    
    def grab_AOI(self, regionNames):
        top = self.detection_rect["height"]
        left = self.detection_rect["width"]
        bottom = 0
        right = 0
        
        if regionNames == "all" : regionNames = config["regions"]

        for region in regionNames:
            rect = config["regions"][region]["2560x1440"]
            if '0' in rect:
                for i in range(0, 4):
                    top = min(top, rect[str(i)]["y"])
                    bottom = max(bottom, rect[str(i)]["y"] + rect["h"])
                    left = min(left, rect[str(i)]["x"])
                    right = max(right, rect[str(i)]["x"] + rect["w"])
                    if config["player"] == 1:
                        print(region)
                        break
            else:
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

    def match_detectables_on_region(self, regionKey, detectableKeys):
        region_rect = config["regions"][regionKey]["2560x1440"]
        crop = self.get_cropped_frame_copy(region_rect)

        filtered_crops = {}
        for d in detectableKeys:
            filt = self.filters.get(d)

            if filt is not None and filt not in filtered_crops:
                filtered_crops[filt] = filt(crop.copy())

        for d in detectableKeys:

            if d in self.filters:
                selected_crop = filtered_crops[self.filters[d]]
            else:
                selected_crop = crop

            max_matches = config["regions"][regionKey].get("MaxMatches", 1)
            if len(config["regions"][regionKey]["Matches"]) >= max_matches:
                break

            if d in self.prompt_detectables:
                # To save performance and avoid false positives: crop the selected crop to the center, to fit the template's width
                template_w = config["detectables"][regionKey][d]["template"].shape[1]
                crop_w = selected_crop.shape[1]
                left = int((crop_w - template_w) / 2)
                right = left + template_w
                left = max(left - 3, 0)
                right = min(right + 3, crop_w)
                selected_crop = selected_crop[:, left:right, :]

            selected_crop = cv.cvtColor(selected_crop, cv.COLOR_BGR2GRAY)
            config["detectables"][regionKey][d]["template"] = cv.cvtColor(config["detectables"][regionKey][d]["template"], cv.COLOR_BGR2GRAY)
            r_shape = selected_crop.shape
            t_shape = config["detectables"][regionKey][d]["template"].shape
            
            if t_shape[0] > r_shape[0] or t_shape[1] > r_shape[1]:
                print("Template {0}({1}) is bigger than region {2}".format(d, t_shape, r_shape))
                return

            match_max_value = self.match_template(selected_crop, config["detectables"][regionKey][d]["template"])
            config["detectables"][regionKey][d]["template"] = cv.cvtColor(config["detectables"][regionKey][d]["template"], cv.COLOR_GRAY2BGR)

            if match_max_value > config["detectables"][regionKey][d]["threshold"]:
                config["detectables"][regionKey][d]["Count"] += 1
                config["regions"][regionKey]["Matches"].append(d)
    
    def match_template(self, frame, template):
        result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
        return maxVal
    
    def scale_rect(self, rect):
        scaled_rect = {
            "x": int (rect["x"] * self.resolution_scaling_factor),
            "y": int (rect["y"] * self.resolution_scaling_factor),
            "w": int (rect["w"] * self.resolution_scaling_factor),
            "h": int (rect["h"] * self.resolution_scaling_factor)
        }
        return scaled_rect

    def get_cropped_frame_copy(self, rect):
        top = rect["y"] - self.frame_offset[0]
        bottom = rect["y"] + rect["h"] - self.frame_offset[0]
        left = rect["x"] - self.frame_offset[1]
        right = rect["x"] + rect["w"] - self.frame_offset[1]
        return self.frame[top:bottom, left:right].copy()

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