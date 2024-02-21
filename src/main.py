# This is a sample Python script.
import os
import sys

from PyQt6.QtQuick import QQuickWindow
from PyQt6.QtWidgets import (
    QApplication,
)

from src.uis.HomeWindow import HomeWindow


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool uis, actions, and settings.


def get_parent_folder():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return curr_dir[:curr_dir.rfind("/")]


def get_asset_folder():
    asset_folder = get_parent_folder() + "/assets"
    return asset_folder


def get_data_folder():
    data_folder = get_parent_folder() + "/data"
    return data_folder


if __name__ == '__main__':
    QQuickWindow.setSceneGraphBackend('software')
    app = QApplication(sys.argv)
    window = HomeWindow(data_dir=get_data_folder(), asset_dir=get_asset_folder())  # SessionWindow(get_asset_folder())
    window.showMaximized()
    window.show()

    sys.exit(app.exec())
    # f = 0
    # while True:
    #     f = (f+1) % 2
    #     print(f"calling toggle-img {f}")
    #     window.toggle_img(f'../ui/assets/dish_mv_rg{f}.png')
    #     time.sleep(0.5)
