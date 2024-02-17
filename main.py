# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import sys
import os
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPalette, QColor, QColorConstants
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtQuick import QQuickWindow
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic.properties import QtCore


def get_img(path):
    lbl = QLabel()
    img = QPixmap(path)
    lbl.setPixmap(img)
    lbl.setScaledContents(True)
    lbl.setMaximumWidth(500)
    lbl.setMaximumHeight(450)
    return lbl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widgets App")
        self.setFixedWidth(800)
        self.setFixedHeight(600)
        self.img_no = 0

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img = get_img('ui/assets/dish_mv_rg1.png')
        self.layout.addWidget(self.lbl_img)

        self.imgUpdateTimer = QTimer(self)
        self.imgUpdateTimer.setInterval(500)  # .5 seconds
        self.imgUpdateTimer.timeout.connect(lambda: self.toggle_img())
        self.imgUpdateTimer.start()

        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        widget.setLayout(self.layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    def toggle_img(self):
        self.img_no = (self.img_no+1) % 2
        path = f"ui/assets/dish_mv_rg{self.img_no}.png"
        self.layout.removeWidget(self.lbl_img)
        self.lbl_img = get_img(path)
        self.layout.addWidget(self.lbl_img)


if __name__ == '__main__':
    QQuickWindow.setSceneGraphBackend('software')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
    # f = 0
    # while True:
    #     f = (f+1) % 2
    #     print(f"calling toggle-img {f}")
    #     window.toggle_img(f'ui/assets/dish_mv_rg{f}.png')
    #     time.sleep(0.5)


