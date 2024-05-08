import sys
import asyncio

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap, QPalette
import numpy as np
import cv2 as cv

from comp_vision import ComputerVision
from overlay import Overlay


class GUI(QMainWindow):
    update_signal = pyqtSignal()

    def __init__(self) -> None:
        super(GUI, self).__init__()
        # load_from_file()
        # save_to_file()

        # Main Window Metadata
        self.setWindowTitle("Practice")  # Title
        self.resize(1200, 1000)  # Window Size
        qApp.setStyleSheet("QWidget{font-size:18px;}")

        # Main Window Layout
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.layout = QGridLayout()
        centralWidget.setLayout(self.layout)

        # Setting Up Tabs, Overlay, Computer Vision
        self.computer_vision = ComputerVision()
        self.overlay = Overlay(self.computer_vision)
        self.mainTab = MainTab(self, self.computer_vision, self.overlay)  # NiL Method
        self.setup_tabs();
        self.show()

        self.update_signal.connect(self.update_graphics)  # Signals Update

        self.backgroud_thread = Worker(self.background_thread_loop)
        self.backgroud_thread.start()

    def setup_tabs(self):
        self.tabs = QTabWidget(self)
        self.layout.addWidget(self.tabs, 0, 0)

        self.underwatch_tab = self.mainTab
        self.tabs.addTab(self.underwatch_tab, "Main Window")

    def closeEvent(self, event):
        self.backgroud_thread.terminate()
        event.accept()

    async def background_thread_loop(self):
        while True:
            cv_updated = self.computer_vision.update()
            if cv_updated:
                self.update_signal.emit()
            await asyncio.sleep(1 / 1000)

    def update_graphics(self):
        if self.computer_vision.resolution_changed:  # Handles Res Change
            self.overlay.close()  # restart
            self.overlay = Overlay(self.computer_vision)  # Reinit
            self.computer_vision.resolution_changed = False

        self.mainTab.update_current_frame()  # Update Main Tab
        self.overlay.update()  # Update the Overlay


class MainTab(QWidget):
    def __init__(self, parent, computer_vision, overlay):
        super(MainTab, self).__init__(parent)
        self.computer_vision = computer_vision
        self.inner_layout = QGridLayout(self)
        self.inner_layout.setAlignment(Qt.AlignTop)
        self.label = QLabel();

        scroll_widget = QWidget(self)
        scroll_widget.setLayout(self.inner_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setBackgroundRole(QPalette.Base)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        outer_layout = QGridLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

    def update_current_frame(self):
        frame, width, height = self.computer_vision.grab_current_frame()  # np array
        qimage = QImage(frame, width, height,
                        QImage.Format_RGB32)
        current_frame = QPixmap(qimage)

        self.label.setPixmap(current_frame)
        self.inner_layout.addWidget(self.label)


class Worker(QThread):
    def __init__(self, funtion):
        super(QThread, self).__init__()
        self.function = funtion

    def run(self):
        asyncio.run(self.function())


app = QApplication(sys.argv)
app_window = GUI()
test = ComputerVision()
app.exec()

try:
    input("Press any key to exit...")
except:
    pass