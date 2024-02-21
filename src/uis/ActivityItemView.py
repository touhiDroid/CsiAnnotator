from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QLabel, QPushButton


class ActivityItemView(QWidget):
    def __init__(self, activity, asset_dir, update_activity_in_expt):
        super(ActivityItemView, self).__init__()
        self.activity = activity
        self.asset_dir = asset_dir
        self.update_activity_in_expt = update_activity_in_expt

        qvb = QVBoxLayout()

        et_title = QLineEdit(activity.name)
        et_title.setMaxLength(40)
        et_title.setFixedHeight(40)
        et_title.textChanged.connect(self.activity_name_changed)
        et_title.setFont(QFont('Courier', 16, 400, False))
        et_title.setFixedSize(450, 48)
        qvb.addWidget(et_title)

        # region : Duration Per Activity
        qhb_dur = QHBoxLayout()
        qlb_dur_title = QLabel("# Duration: ")
        qlb_dur_title.setFont(QFont('Courier', 18, 400, False))
        qlb_dur_title.setFixedSize(200, 48)
        qhb_dur.addWidget(qlb_dur_title)

        qlb_dur = QLabel(str(activity.duration_secs))
        qlb_dur.setStyleSheet("color: black;")
        qlb_dur.setFixedSize(48, 32)

        btn_subtract_dur_secs = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/subtract.png"))
        btn_subtract_dur_secs.setFixedSize(32, 32)
        btn_subtract_dur_secs.clicked.connect(lambda: self.dur_subtract_clicked(qlb_dur))
        qhb_dur.addWidget(btn_subtract_dur_secs)

        qhb_dur.addWidget(qlb_dur)

        btn_add_dur_secs = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/add.png"))
        btn_add_dur_secs.setFixedSize(32, 32)
        btn_add_dur_secs.clicked.connect(lambda: self.dur_add_clicked(qlb_dur))
        qhb_dur.addWidget(btn_add_dur_secs)

        qhb_dur.setAlignment(Qt.AlignmentFlag.AlignLeft)
        qvb.addLayout(qhb_dur)
        # endregion : Reps. Per Activity

        qhb_img = QHBoxLayout()
        btn_img1 = QPushButton(text='Primary Image', icon=QIcon(f"{self.asset_dir}/icons/activity_image.png"))
        btn_img1.setFixedHeight(40)
        btn_img1.clicked.connect(lambda: self.add_image1(btn_img1))
        qhb_img.addWidget(btn_img1)

        btn_img2 = QPushButton(text='Secondary Image', icon=QIcon(f"{self.asset_dir}/icons/activity_image.png"))
        btn_img2.setFixedHeight(40)
        btn_img2.clicked.connect(lambda: self.add_image2(btn_img2))
        qhb_img.addWidget(btn_img2)
        qvb.addLayout(qhb_img)

        self.setLayout(qvb)
        # self.setMinimumHeight(600)

    def activity_name_changed(self, new_name):
        self.activity.name = new_name
        self.update_activity_in_expt(self.activity)

    def dur_subtract_clicked(self, qlb_dur):
        print(f"TODO Show on UI & save into JSON file saying one-LESS duration second for '{self.activity.name}'")
        if self.activity.duration_secs <= 1:
            return
        self.activity.duration_secs -= 1
        qlb_dur.setText(str(self.activity.duration_secs))
        # self.experiment.activities[a.id == activity.id for a in self.experiment.activities].duration_secs = activity.duration_secs
        self.update_activity_in_expt(self.activity)

    def dur_add_clicked(self, qlb_dur):
        print(f"TODO Show on UI & save into JSON file saying one-MORE duration second for '{self.activity.name}'")
        self.activity.duration_secs += 1
        qlb_dur.setText(str(self.activity.duration_secs))
        self.update_activity_in_expt(self.activity)

    def add_image1(self, btn_img1):
        # TODO Show file chooser & copy img-file to /assets
        print("# TODO Show file chooser & copy primary img-file to /assets")

    def add_image2(self, btn_img2):
        # TODO Show file chooser & copy img-file to /assets
        print("# TODO Show file chooser & copy secondary img-file to /assets")

