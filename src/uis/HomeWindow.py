import json

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QIcon, QFontDatabase
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QListWidget, QLabel, QAbstractItemView, \
    QPushButton, QVBoxLayout, QHBoxLayout

from src.models.Experiment import Experiment
from src.uis.ExptDetailsView import ExptDetailsView


class HomeWindow(QMainWindow):
    def __init__(self, data_dir, asset_dir):
        super().__init__()
        self.data_dir = data_dir
        self.asset_dir = asset_dir
        self.setWindowTitle("CSI Annotator")
        self.asset_dir = asset_dir
        # setting geometry
        # self.setGeometry(100, 100, 600, 400)

        parent_lt = QGridLayout()

        q_label_expt = QLabel("Experiments")
        print(q_label_expt.font().family())
        q_label_expt.setFont(QFont('Courier', 32, 800, False))
        q_label_expt.setStyleSheet("background-color: orange; color: black;")
        parent_lt.addWidget(q_label_expt, 0, 0, 1, 1)

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
        expt_list.setFont(QFont('Courier', 20, 500, True))
        expt_list.setStyleSheet("color: black; padding: 0px;")  # background-color: yellow;
        expt_list.setSpacing(0)
        parent_lt.addWidget(expt_list, 1, 0, 10, 1)

        btn_add_expt = QPushButton(icon=QIcon(f"{asset_dir}/icons/add.png"), text="Add New Experiment", parent=self)
        btn_add_expt.setFixedSize(300, 60)
        btn_add_expt.setIconSize(QSize(32, 32))
        btn_add_expt.setStyleSheet("color: black; padding: 5px;")
        parent_lt.addWidget(btn_add_expt, 12, 0, 1, 1)

        self.qvl_expt_details = QVBoxLayout()
        self.expt_details_view = ExptDetailsView(self.experiments[expt_list.currentRow()], self.asset_dir)
        self.expt_details_view.setStyleSheet("color: black;")  # background-color: #F7F7F7;
        self.qvl_expt_details.addWidget(self.expt_details_view)
        parent_lt.addLayout(self.qvl_expt_details, 0, 1, 10, 40)

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
