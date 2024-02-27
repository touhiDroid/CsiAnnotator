import json

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QListWidget, QLabel, QAbstractItemView, \
    QPushButton, QVBoxLayout, QInputDialog, QScrollArea

from src.helpers import big_action_button_style, show_under_construction_message, api
from src.models.Experiment import Experiment
from src.uis.ExptDetailsView import ExptDetailsView


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class HomeWindow(QMainWindow):
    def __init__(self, data_dir, asset_dir):
        super().__init__()
        self.data_dir = data_dir
        self.asset_dir = asset_dir
        self.setWindowTitle("CSI Annotator")
        self.setWindowIcon(QIcon(f"{asset_dir}/icons/app_icon.png"))
        self.asset_dir = asset_dir
        # setting geometry
        # self.setGeometry(100, 100, 600, 400)

        parent_lt = QGridLayout()

        qlb_server_title = QLabel("\u25BC Server Info")
        qlb_server_title.setFont(QFont('Courier', 24, 800, False))
        qlb_server_title.setStyleSheet("color: black;")  # background-color: orange;
        parent_lt.addWidget(qlb_server_title, 0, 0, 1, 1)

        scroll_area = QScrollArea()
        self.qlb_server_info = QLabel("Hostname: raspi.local\nData Dir.: ../1709398572.130102\nDevices:" +
                                      "\n1. ttyUSB0: Ch-6, 999MB, 100Hz" +
                                      "\n2. ttyUSB1: Ch-11, 999MB, 100Hz\n")  # TODO query server & device info
        self.qlb_server_info.setFont(QFont('Courier', 13, 800, False))
        self.qlb_server_info.setStyleSheet("color: black;")  # background-color: orange;
        self.qlb_server_info.setWordWrap(True)
        scroll_area.setWidget(self.qlb_server_info)
        scroll_area.setMaximumWidth(300)
        parent_lt.addWidget(scroll_area, 1, 0, 2, 1)

        btn_server = QPushButton(text="Edit Server URL")
        btn_server.setFixedSize(300, 48)
        btn_server.setStyleSheet(big_action_button_style())
        btn_server.clicked.connect(self.edit_server_clicked)
        parent_lt.addWidget(btn_server, 3, 0, 1, 1)

        q_label_expt = QLabel("\u25BC Experiments")
        q_label_expt.setFont(QFont('Courier', 24, 800, False))
        q_label_expt.setStyleSheet("color: black;")  # background-color: orange;
        parent_lt.addWidget(q_label_expt, 4, 0, 1, 1)

        self.experiments = Experiment.list_from_json(json.load(open(f"{data_dir}/data.json"))['experiments'])
        expt_list = QListWidget()
        expt_list.setSelectionRectVisible(True)
        expt_list.setWordWrap(True)
        expt_list.setMaximumWidth(300)
        expt_list.setUniformItemSizes(True)
        expt_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        expt_list.addItems(Experiment.to_name_list(self.experiments))
        # expt_list.currentItemChanged.connect(self.expt_changed)
        # noinspection PyUnresolvedReferences
        expt_list.currentTextChanged.connect(self.expt_name_changed)
        expt_list.setCurrentRow(0)
        expt_list.setFont(QFont('Courier', 16, 500, True))
        expt_list.setStyleSheet("color: black; padding: 0px;")  # background-color: yellow;
        expt_list.setSpacing(0)
        parent_lt.addWidget(expt_list, 5, 0, 8, 1)

        btn_add_expt = QPushButton(icon=QIcon(f"{asset_dir}/icons/add.png"), text="Add New Experiment", parent=self)
        btn_add_expt.setFixedSize(300, 54)
        btn_add_expt.setIconSize(QSize(28, 28))
        btn_add_expt.setStyleSheet(big_action_button_style())
        btn_add_expt.clicked.connect(self.add_expt_clicked)
        parent_lt.addWidget(btn_add_expt, 13, 0, 1, 1)

        sep_color = Color("#0C0D0F")
        sep_color.setFixedWidth(1)
        parent_lt.addWidget(sep_color, 0, 1, 14, 1)

        self.qvl_expt_details = QVBoxLayout()
        self.expt_details_view = ExptDetailsView(self.experiments[expt_list.currentRow()], self.asset_dir)
        self.qvl_expt_details.addWidget(self.expt_details_view)
        parent_lt.addLayout(self.qvl_expt_details, 0, 2, 14, 40)

        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        widget.setLayout(parent_lt)
        self.setCentralWidget(widget)

    # def expt_changed(self, item):
    #     print(item.text())

    def expt_name_changed(self, expt_name):
        try:
            self.qvl_expt_details.removeWidget(self.expt_details_view)
            expt = None
            for e in self.experiments:
                if e.name == expt_name:
                    expt = e
                    break
            self.expt_details_view = ExptDetailsView(expt, self.asset_dir)
            self.expt_details_view.setStyleSheet("color: black;")
            self.qvl_expt_details.addWidget(self.expt_details_view)
        except AttributeError as ae:
            print(ae)

    def edit_server_clicked(self):
        new_host, ok = QInputDialog.getText(self, 'Server Host', 'Host-name:', text=api.get_server_host())
        if ok:
            api.update_server_host(new_host)

    def add_expt_clicked(self):
        # TODO Add experiment
        show_under_construction_message(self.asset_dir)
