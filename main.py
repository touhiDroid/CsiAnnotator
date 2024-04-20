# This is a sample Python script.
import logging
import warnings
import os
import sys

from PyQt5.QtQuick import QQuickWindow
from PyQt5.QtWidgets import (
    QApplication,
)

from src.uis.HomeWindow import HomeWindow


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool uis, actions, and settings.


def get_app_dir():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return curr_dir  # [:curr_dir.rfind("/")]


def get_asset_dir():
    asset_dir = get_app_dir() + "/assets"
    return asset_dir


def get_data_dir():
    data_dir = get_app_dir() + "/data"
    return data_dir


def filter_pyqt5_warnings(record):
    if "QFont::setPixelSize: Pixel size <= 0 (0)" in record.msg:
        return False
    return True


class FontWarningHandler(Warning):
    def emit(self, record):
        if "QFont::setPixelSize: Pixel size <= 0 (0)" in record.msg:
            pass
        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    logging.getLogger().addFilter(filter_pyqt5_warnings)
    warnings.filterwarnings("ignore", category=FontWarningHandler)

    QQuickWindow.setSceneGraphBackend('software')
    app = QApplication(sys.argv)
    window = HomeWindow(data_dir=get_data_dir(), asset_dir=get_asset_dir())  # SessionWindow(get_asset_folder())
    window.showMaximized()
    window.show()

    sys.exit(app.exec())
    # f = 0
    # while True:
    #     f = (f+1) % 2
    #     print(f"calling toggle-img {f}")
    #     window.toggle_img(f'../ui/assets/dish_mv_rg{f}.png')
    #     time.sleep(0.5)
