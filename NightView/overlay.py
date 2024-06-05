from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap
from win32gui import GetWindowText, GetForegroundWindow

from config_table import config


class Overlay(QWidget):
    def __init__(self, computer_vision) -> None:
        super(Overlay, self).__init__(parent=None)
        self.cv = computer_vision
        self.aspectRatio = "2560x1440"
        self.setWindowTitle("overlay")

        # Hides the window from the taskbar
        flags = 0
        flags |= Qt.WindowType.WindowTransparentForInput
        flags |= Qt.WindowStaysOnTopHint
        flags |= Qt.FramelessWindowHint
        flags |= Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_elements()
        self.update_geometry()
        self.show()
        self.update()

    def setup_elements(self):
        # Line Corners of Overlay with a 1 pixel Solid Magenta line
        self.corners = QLabel("", self)
        self.corners.setStyleSheet("border: 1px solid magenta;")
        if config["player"]:
            # The Red Detection Regions, Red Outline + Title
            self.regions = {}
            for region in config["regions"]:  # Get Regions from config list in config_handler
                if '0' in config["regions"][region]["2560x1440"]:
                    self.regions[region] = {}
                    for i in range(0, 4):
                        # Red Outline
                        rect = QLabel("", self)
                        rect.setStyleSheet("color: red; border: 1px solid red;")
                        # Red Title
                        label = QLabel(region, self)
                        label.setStyleSheet("color: red; font: bold 14px;")

                        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

                        self.regions[region][str(i)] = {"Rect": rect, "Label": label}
                        if region == "Survivors": break
                else:
                    # Red Outline
                    rect = QLabel("", self)
                    rect.setStyleSheet("color: red; border: 1px solid red;")
                    # Red Title
                    label = QLabel(region, self)
                    label.setStyleSheet("color: red; font: bold 14px;")

                    label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    self.regions[region] = {"Rect": rect, "Label": label}  # Add region to list of regions
        else:
            self.regions = {}
            region = "player_type"
            rect = QLabel("", self)
            rect.setStyleSheet("color: red; border: 1px solid red;")
            # Red Title
            label = QLabel(region, self)
            label.setStyleSheet("color: red; font: bold 14px;")

            label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.regions[region] = {"Rect": rect, "Label": label}  # Add region to list of regions

    def update_geometry(self):
        self.setGeometry(
            self.cv.detection_rect["left"],
            self.cv.detection_rect["top"],
            self.cv.detection_rect["width"],
            self.cv.detection_rect["height"]
        )
        # Set Corners, aka, Covers Entire Width/Height of screen
        self.corners.setGeometry(
            0,
            0,
            self.cv.detection_rect["width"],  # Detects ASpect Ratio from Monitor
            self.cv.detection_rect["height"]
        )

        # Setting rectangles for regions/Detectables self.regions[region][str(i)]
        for region in config["regions"]:
            scaled_rect = config["regions"][region]["2560x1440"]  # Get Aspect Ratio, Created in CV(?)
            tempwidth = scaled_rect["w"] + 2
            tempheight = scaled_rect["h"] + 2

            if '0' in scaled_rect:
                for i in range(0, 4):
                    self.regions[region][str(i)]["Rect"].setGeometry(
                        scaled_rect[str(i)]["x"] - 1,
                        scaled_rect[str(i)]["y"] - 1,
                        tempwidth,
                        tempheight
                    )
                    self.regions[region][str(i)]["Label"].setGeometry(
                        scaled_rect[str(i)]["x"],
                        scaled_rect[str(i)]["y"],
                        100,
                        20
                    )
                    break
            else:
                self.regions[region]["Rect"].setGeometry(
                    scaled_rect["x"] - 1,
                    scaled_rect["y"] - 1,
                    tempwidth,
                    tempheight
                )
                self.regions[region]["Label"].setGeometry(
                    scaled_rect["x"],
                    scaled_rect["y"],
                    200,
                    100
                )

    def update(self):
        self.set_active(True)
        self.update_regions()

    # Show Overlay
    def set_active(self, value):
        if value is False:
            self.corners.hide()
            for region in self.regions:
                if type(region) is list:
                    for i in range(0, 4):
                        self.regions[region][str(i)]["Rect"].hide()
                        self.regions[region][str(i)]["Label"].setText("")
                else:
                    self.regions[region]["Rect"].hide()
                    self.regions[region]["Label"].setText("")
        else:
            self.corners.show()

    def update_regions(self):
        for region in self.regions:
            if '0' in self.regions[region]:
                for i in range(0, 4):
                    current = self.regions[region][str(i)]["Rect"]
                    current.show()
                    self.regions[region][str(i)]["Label"].show()
                    self.regions[region][str(i)]["Label"].setText(region + "_" + str(i))
                    if region == "Survivors" : break
            else:
                self.regions[region]["Rect"].show()
                self.regions[region]["Label"].show()
                self.regions[region]["Label"].setText(region)
