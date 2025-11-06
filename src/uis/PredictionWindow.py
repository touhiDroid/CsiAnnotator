from collections import deque
from datetime import datetime

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QDesktopWidget, QWidget, QHBoxLayout

from src.helpers import api, format_bytes
from src.helpers.app_cache import AppCache, ServerStatus
from src.models.EspDevice import EspDevice
from src.uis.CsiDataGraphWidget import CsiDataGraphWidget


# def get_recent_data(device):
#     d = api.get_device_data(device.name, duration=60)
#     if d is not None and d.file_size > 0 and d.tx_rate > 0:
#         return d.live_data
#     return None


def get_data_rate(device):
    d = api.get_esp_device_details(device.name)
    if d is not None:
        return d.tx_rate
    return None


class TimerThread(QThread):
    tick = pyqtSignal()

    def __init__(self, interval_ms=500, parent=None):
        super().__init__(parent)
        self.interval_ms = interval_ms
        self._running = True

    def run(self):
        while self._running:
            self.msleep(self.interval_ms)
            self.tick.emit()

    def stop(self):
        self._running = False
        self.wait()


class PredictionWindow(QMainWindow):
    def __init__(self, experiment, asset_dir, prediction_duration=120):
        super().__init__()
        self.app_cache = AppCache()
        self.setWindowTitle(experiment.name)
        self.setWindowIcon(QIcon(f"{asset_dir}/icons/app_icon.png"))
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowFullScreen)
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(screen_geometry)
        self.showFullScreen()
        # print("Chk-1")

        self.experiment = experiment
        self.asset_dir = asset_dir
        self.prediction_duration = prediction_duration
        self.session_start_time = datetime.now()
        self.last_predictions = deque([0.0] * self.prediction_duration, maxlen=self.prediction_duration)

        qvl_parent = QVBoxLayout()
        qvl_parent.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        server_status_color = self.get_server_info_text_color()
        self.qlb_server_stat_top = QLabel("<<Server Info>>")
        self.qlb_server_stat_top.setFont(QFont('Courier', 24, 800, False))
        self.qlb_server_stat_top.setStyleSheet(f"padding: 6px;color: {server_status_color};")
        self.qlb_server_stat_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qvl_parent.addWidget(self.qlb_server_stat_top)

        self.qlb_device_info_top = QLabel("<<Device Info>>")
        self.qlb_device_info_top.setFont(QFont('Courier', 16, 400, False))
        self.qlb_device_info_top.setStyleSheet(f"padding: 6px;color: {server_status_color};")
        self.qlb_device_info_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qvl_parent.addWidget(self.qlb_device_info_top)

        server_ret_tuple = self.get_server_info()
        if server_ret_tuple is not None:
            server_info, devices_str, device_list = server_ret_tuple
            self.qlb_server_stat_top.setText(server_info)
            self.qlb_device_info_top.setText(devices_str)

            qhl_csi_graphs = QHBoxLayout()
            self.csi_data_widgets = []
            for device in device_list:
                print(device.get_str())
                csi_data_widget = CsiDataGraphWidget(device)
                qhl_csi_graphs.addWidget(csi_data_widget)
                self.csi_data_widgets.append(csi_data_widget)
                tx_rate = get_data_rate(device)
                csi_data_widget.set_data(tx_rate)
            qvl_parent.addLayout(qhl_csi_graphs)

        self.qlb_prediction = QLabel("Predicted Action")
        self.qlb_prediction.setFont(QFont('Courier', 32, 100, False))
        self.qlb_prediction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qlb_prediction.setStyleSheet('padding: 16px;background:white;')
        qvl_parent.addWidget(self.qlb_prediction)

        self.pg_predict = pg.PlotWidget()
        self.pg_predict.showGrid(x=True, y=True)
        self.pg_predict.setBackground('w')
        self.pg_predict.setLabel('left', 'Predicted Action')
        self.pg_predict.setLabel("bottom", "Time (last 2 minutes)")
        self.actions = [(0, 'Stationary'), (1, 'Left-Right'), (2, 'Up-Down'), (3, 'Wave')]
        self.pg_predict.getAxis('left').setTicks([self.actions])
        self.pg_predict.setYRange(0, 4)
        self.pg_predict.setTitle(f"Real-Time Action Prediction Using CSI Amplitudes")
        qvl_parent.addWidget(self.pg_predict)

        # --- Plot curve ---
        self.predict_curve = self.pg_predict.plot(
            np.arange(120), self.get_prediction_list(), pen=pg.mkPen('r', width=2)
        )

        self.timer_thread = TimerThread(500)
        self.timer_thread.tick.connect(self.update_graphs)
        self.timer_thread.start()

        widget = QWidget()
        widget.setStyleSheet("background-color: white; color: black;")
        widget.setLayout(qvl_parent)
        self.setCentralWidget(widget)

    def update_graphs(self):
        for csi_data_rate_graph in self.csi_data_widgets:
            csi_data_rate_graph.set_data(get_data_rate(csi_data_rate_graph.device))

        choice = np.random.choice([0, 1, 2, 3])  # FIXME
        predicted_action_name = self.actions[choice][-1]
        self.qlb_prediction.setText(predicted_action_name)
        self.last_predictions.append(choice)
        self.predict_curve.setData(self.get_prediction_list())

        server_ret_tuple = self.get_server_info()
        if server_ret_tuple is not None:
            server_info, devices_str, device_list = server_ret_tuple
            self.qlb_server_stat_top.setText(server_info)
            self.qlb_device_info_top.setText(devices_str)

    def get_server_info_text_color(self):
        if self.app_cache.missed_server_calls > 5:
            self.app_cache.server_status = ServerStatus.GONE
        elif self.app_cache.missed_server_calls > 3:
            self.app_cache.server_status = ServerStatus.GOING
        elif self.app_cache.missed_server_calls >= 0:
            self.app_cache.server_status = ServerStatus.OK
        else:
            self.app_cache.server_status = ServerStatus.NONE
        return "green" if self.app_cache.server_status == ServerStatus.OK else (
            "orange" if self.app_cache.server_status == ServerStatus.GOING else (
                "red" if self.app_cache.server_status == ServerStatus.GONE else "black"))

    def get_prediction_list(self):
        return list(self.last_predictions)

    def get_server_info(self):
        host = api.get_server_host()
        # self.app_cache.server_stats = self.app_cache.server_stats
        if self.app_cache.server_stats is None:
            return None
        data_dir, used_bytes, total_bytes, device_names = self.app_cache.server_stats
        devices = []
        for dn in device_names:
            device = api.get_esp_device_details(dn)
            if device is not None and device.file_size > 0 and device.tx_rate > 0:
                devices.append(device)
        try:
            data_dir_name = data_dir[data_dir[:-2].rindex('/'):len(data_dir) - 1]
        except Exception as e:
            print(e)
            data_dir_name = ''
        return (
            f"\u21F0 Server: {host} \t \u21F0 Storage: {format_bytes(used_bytes)} / {format_bytes(total_bytes)} \t \u21F0 Data Dir.:\n ..{data_dir_name}"), f"\u21F0 Devices with CSI:\n{EspDevice.get_list_to_str(devices)}", devices

    def set_server_info(self):
        server_info, device_info = self.get_server_info()
        if server_info is not None:
            self.qlb_server_stat_left.setText(server_info)
        if device_info is not None:
            self.qlb_device_info_top.setText(device_info)
        # self.qlb_server_info.setFont(QFont('Courier', 13, 800 if self.binary_toggler == 0 else 400, False))
        color = self.get_server_info_text_color()
        self.qlb_server_stat_left.setStyleSheet(f"color: {color};")  # background-color: orange;
        self.qlb_device_info_top.setStyleSheet(f"color: {color};")  # background-color: orange;
