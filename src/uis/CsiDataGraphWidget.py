from collections import deque

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from src.models.EspDevice import EspDevice


class CsiDataGraphWidget(QWidget):
    def __init__(self, device, window_size=120):
        super().__init__()

        self.setWindowTitle("ESP32 Data Rates")
        self.setGeometry(0, 0, 300, 200)
        self.device = device
        self.window_size = window_size  # e.g., 120 points → 2 minutes if updated per second

        layout = QVBoxLayout()

        # --- Graph Widget setup ---
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', 'Data Rate (Hz)')
        self.plot_widget.setLabel("bottom", "Time (last 2 minutes)")
        self.plot_widget.setYRange(0, 120)
        self.plot_widget.setTitle(f"{device.name}: Real-Time CSI Data Rate (Hz)")
        layout.addWidget(self.plot_widget)

        # Device info
        self.qlb_device_info = QLabel("<<Device Info>>")
        self.qlb_device_info.setFont(QFont('Courier', 12, 400, False))
        self.qlb_device_info.setStyleSheet('padding: 6px;')
        self.qlb_device_info.setText(self.device.get_str())
        layout.addWidget(self.qlb_device_info, Qt.AlignmentFlag.AlignTop)

        # --- Internal buffer (fixed-length) ---
        self.data_rates = deque([0.0] * self.window_size, maxlen=self.window_size)

        # --- Plot curve ---
        self.curve = self.plot_widget.plot(
            np.arange(self.window_size),
            list(self.data_rates),
            pen=pg.mkPen('r', width=2)
        )

        # Layout container
        self.setLayout(layout)
        self.setStyleSheet("color: white;")

    def set_data(self, current_data_rate: float):
        """
        Push a new data rate value and update the plot.
        Args:
            current_data_rate (float): The most recent data rate in Hz (0–110 typical)
        """
        try:
            val = float(current_data_rate)
        except (TypeError, ValueError):
            val = 0.0

        self.data_rates.append(val)
        self.curve.setData(list(self.data_rates))


# --- Optional: Test/Demo Code ---
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys, random

    # Simulate 60 seconds worth of CSI timestamps (~100Hz)
    base_ts = 1762448874121.127
    lines = []
    for i in range(6000):
        ts = base_ts + i * (1000.0 / (100 + random.uniform(-5, 5)))  # simulate jittered 100Hz
        lines.append(
            f"CSI_DATA,AP,FC:B4:67:74:07:90,-70,11,1,2,1,1,1,0,0,0,0,-91,0,5,1,2131420658,0,84,0,0,6426.58,384,[84 -64 ...],fake_uuid,{ts},default_experiment_name"
        )

    app = QApplication(sys.argv)
    graph = CsiDataGraphWidget(EspDevice("/dev/ttyUSB0", 7, 100, 1000))
    graph.show()
    graph.set_data(lines)
    sys.exit(app.exec_())
