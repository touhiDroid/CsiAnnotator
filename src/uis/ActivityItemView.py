from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QLabel, QPushButton

from src.helpers import icon_only_button_style, show_under_construction_message


class ActivityItemView(QWidget):
    def __init__(self, serial, activity, asset_dir, update_activity_in_expt, color_str, item_deleted):
        super(ActivityItemView, self).__init__()
        self.activity = activity
        self.asset_dir = asset_dir
        self.update_activity_in_expt = update_activity_in_expt
        self.item_deleted = item_deleted

        qvb = QVBoxLayout()

        qhb_title = QHBoxLayout()
        qlb_serial = QLabel(str(serial) + '#')
        qlb_serial.setStyleSheet("background-color: " + color_str + "; border: 1px solid black; border-radius: 16px;")
        qlb_serial.setFont(QFont('Courier', 16, 400, False))
        qhb_title.addWidget(qlb_serial)

        et_title = QLineEdit(activity.name)
        et_title.setMaxLength(40)
        et_title.setFixedHeight(40)
        et_title.textChanged.connect(self.activity_name_changed)
        et_title.setFont(QFont('Courier', 16, 400, False))
        et_title.setStyleSheet("border-style: 1px solid #ccc!important; border-radius: 8px;")
        et_title.setFixedSize(450, 40)
        qhb_title.addWidget(et_title)

        btn_delete = QPushButton(icon=QIcon(f"{asset_dir}/icons/delete.png"))
        btn_delete.setFixedSize(32, 32)
        btn_delete.setStyleSheet(icon_only_button_style())
        btn_delete.clicked.connect(lambda: self.delete_activity(serial))
        qhb_title.addStretch(1)
        qhb_title.addWidget(btn_delete)
        qvb.addLayout(qhb_title)

        # region : Duration Per Activity
        qhb_dur = QHBoxLayout()
        qlb_dur_title = QLabel("# Duration: ")
        qlb_dur_title.setFont(QFont('Courier', 16, 400, False))
        qlb_dur_title.setStyleSheet("background-color: transparent;")
        qlb_dur_title.setFixedSize(120, 32)
        qhb_dur.addWidget(qlb_dur_title)

        qlb_dur = QLabel(str(activity.duration_secs))
        qlb_dur.setFont(QFont('Courier', 16, 400, False))
        qlb_dur.setStyleSheet("background-color: transparent; color: black;")
        qlb_dur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qlb_dur.setFixedSize(32, 32)

        btn_subtract_dur_secs = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/subtract.png"))
        btn_subtract_dur_secs.setFixedSize(32, 32)
        btn_subtract_dur_secs.clicked.connect(lambda: self.dur_subtract_clicked(qlb_dur))
        btn_subtract_dur_secs.setStyleSheet(icon_only_button_style())
        qhb_dur.addWidget(btn_subtract_dur_secs)

        qhb_dur.addWidget(qlb_dur)

        btn_add_dur_secs = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/add.png"))
        btn_add_dur_secs.setFixedSize(32, 32)
        btn_add_dur_secs.clicked.connect(lambda: self.dur_add_clicked(qlb_dur))
        btn_add_dur_secs.setStyleSheet(icon_only_button_style())
        qhb_dur.addWidget(btn_add_dur_secs)

        qhb_dur.setAlignment(Qt.AlignmentFlag.AlignLeft)
        qvb.addLayout(qhb_dur)
        # endregion : Reps. Per Activity

        qhb_img = QHBoxLayout()
        img1_text = self.activity.img1 if len(self.activity.img1) > 0 else 'Primary Image'
        btn_img1 = QPushButton(text=img1_text, icon=QIcon(f"{self.asset_dir}/icons/activity_image.png"))
        btn_img1.setFixedHeight(40)
        btn_img1.clicked.connect(lambda: self.add_image1(btn_img1))
        qhb_img.addWidget(btn_img1)

        img2_text = self.activity.img2 if len(self.activity.img2) > 0 else 'Secondary Image'
        btn_img2 = QPushButton(text=img2_text, icon=QIcon(f"{self.asset_dir}/icons/activity_image.png"))
        btn_img2.setFixedHeight(40)
        btn_img2.clicked.connect(lambda: self.add_image2(btn_img2))
        qhb_img.addWidget(btn_img2)
        qvb.addLayout(qhb_img)

        self.setLayout(qvb)
        # self.setMinimumHeight(600)

    def delete_activity(self, serial):
        self.item_deleted(self.activity, serial)

    def activity_name_changed(self, new_name):
        self.activity.name = new_name
        self.update_activity_in_expt(self.activity)

    def dur_subtract_clicked(self, qlb_dur):
        if self.activity.duration_secs <= 1:
            return
        self.activity.duration_secs -= 1
        qlb_dur.setText(str(self.activity.duration_secs))
        # self.experiment.activities[a.id == activity.id for a in self.experiment.activities].duration_secs = activity.duration_secs
        self.update_activity_in_expt(self.activity)

    def dur_add_clicked(self, qlb_dur):
        self.activity.duration_secs += 1
        qlb_dur.setText(str(self.activity.duration_secs))
        self.update_activity_in_expt(self.activity)

    def add_image1(self, btn_img1):
        # TODO Show file chooser & copy img-file to /assets
        show_under_construction_message(self.asset_dir)

    def add_image2(self, btn_img2):
        # TODO Show file chooser & copy img-file to /assets
        show_under_construction_message(self.asset_dir)
