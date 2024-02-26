import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, \
    QListWidgetItem, QInputDialog

from src.helpers import big_action_button_style, icon_only_button_style, api, show_under_construction_message
from src.uis.ActivityItemView import ActivityItemView
from src.uis.SessionWindow import SessionWindow


# noinspection PyMethodMayBeStatic
class ExptDetailsView(QWidget):
    def __init__(self, experiment, asset_dir):
        super().__init__()
        self.experiment = experiment
        self.asset_dir = asset_dir
        qvl_parent = QVBoxLayout()

        # region : Top horizontal box
        qh_title = QHBoxLayout()
        et_expt_name = QLineEdit(self.experiment.name)
        et_expt_name.setMaxLength(20)
        et_expt_name.setFixedHeight(40)
        et_expt_name.setFont(QFont('Courier', 17, 400))
        et_expt_name.setPlaceholderText("Experiment Name")
        et_expt_name.setStyleSheet("color: black; background-color: #CCDDFA; "
                                   + "padding: 5px; border-style: 2px solid #000000; border-radius: 8px;")
        et_expt_name.textChanged.connect(self.expt_name_changed)
        self.title_change_ems = 0
        qh_title.addWidget(et_expt_name)

        btn_start = QPushButton("Start Experiment")
        btn_start.setFixedSize(180, 48)
        btn_start.setStyleSheet(big_action_button_style())
        btn_start.clicked.connect(self.start_expt_session)
        qh_title.addWidget(btn_start)

        btn_delete = QPushButton(icon=QIcon(f"{asset_dir}/icons/delete.png"))
        btn_delete.setFixedSize(40, 40)
        btn_delete.setStyleSheet(icon_only_button_style())
        btn_delete.clicked.connect(self.delete_expt)
        qh_title.addWidget(btn_delete)

        qvl_parent.addLayout(qh_title)
        # endregion : Top Horizontal Box

        # region : Transition Time
        qh_tr_time = QHBoxLayout()
        qlb_tr_time_title = QLabel("# Transition Time: ")
        qlb_tr_time_title.setFont(QFont('Courier', 16, 300, False))
        qlb_tr_time_title.setFixedSize(360, 48)
        qh_tr_time.addWidget(qlb_tr_time_title)

        btn_subtract_tr_secs = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/subtract.png"))
        btn_subtract_tr_secs.setFixedSize(32, 32)
        btn_subtract_tr_secs.clicked.connect(self.transition_secs_subtract_clicked)
        btn_subtract_tr_secs.setStyleSheet(icon_only_button_style())
        qh_tr_time.addWidget(btn_subtract_tr_secs)

        self.qlb_tr_secs = QLabel(str(self.experiment.transition_secs))
        self.qlb_tr_secs.setFont(QFont('Courier', 16, 400, False))
        self.qlb_tr_secs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qlb_tr_secs.setStyleSheet("color: black;")
        self.qlb_tr_secs.setFixedSize(32, 32)
        qh_tr_time.addWidget(self.qlb_tr_secs)

        btn_add_tr_secs = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/add.png"))
        btn_add_tr_secs.setFixedSize(32, 32)
        btn_add_tr_secs.clicked.connect(self.transition_secs_add_clicked)
        btn_add_tr_secs.setStyleSheet(icon_only_button_style())
        qh_tr_time.addWidget(btn_add_tr_secs)

        qh_tr_time.setAlignment(Qt.AlignmentFlag.AlignLeft)
        qvl_parent.addLayout(qh_tr_time)
        # endregion : transition time

        # region : Reps. Per Activity
        qh_reps = QHBoxLayout()
        qlb_reps_title = QLabel("# Repetitions Per Activity: ")
        qlb_reps_title.setFont(QFont('Courier', 16, 300, False))
        qlb_reps_title.setFixedSize(360, 48)
        qh_reps.addWidget(qlb_reps_title)

        btn_subtract_reps = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/subtract.png"))
        btn_subtract_reps.setFixedSize(32, 32)
        btn_subtract_reps.clicked.connect(self.reps_subtract_clicked)
        btn_subtract_reps.setStyleSheet(icon_only_button_style())
        qh_reps.addWidget(btn_subtract_reps)

        self.qlb_reps = QLabel(str(self.experiment.reps_per_activity))
        self.qlb_reps.setFont(QFont('Courier', 16, 400, False))
        self.qlb_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qlb_reps.setStyleSheet("color: black;")
        self.qlb_reps.setFixedSize(32, 32)
        qh_reps.addWidget(self.qlb_reps)

        btn_add_reps = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/add.png"))
        btn_add_reps.setFixedSize(32, 32)
        btn_add_reps.clicked.connect(self.reps_add_clicked)
        btn_add_reps.setStyleSheet(icon_only_button_style())
        qh_reps.addWidget(btn_add_reps)

        qh_reps.setAlignment(Qt.AlignmentFlag.AlignLeft)
        qvl_parent.addLayout(qh_reps)
        # endregion : Reps. Per Activity

        # region : Activity Listing
        # qsa_activities = QScrollArea()
        # qvb_activities = QVBoxLayout()

        qlb_activities_title = QLabel("# Activities: ")
        qlb_activities_title.setFont(QFont('Courier', 16, 400, False))
        qlb_activities_title.setFixedSize(300, 48)
        qvl_parent.addWidget(qlb_activities_title)

        self.qlist_activities = QListWidget()
        self.activity_colors = ["#E5E5F5", "#FEEAEA"]
        idx = 1
        for act in self.experiment.activities:
            list_item_view = ActivityItemView(idx, act, self.asset_dir, self.update_activity_in_expt,
                                              self.activity_colors[idx % 2], self.activity_item_deleted)
            ql_widget = QListWidgetItem(self.qlist_activities)
            ql_widget.setSizeHint(list_item_view.sizeHint())
            ql_widget.setBackground(QColor(self.activity_colors[idx % 2]))
            idx += 1

            self.qlist_activities.addItem(ql_widget)
            self.qlist_activities.setItemWidget(ql_widget, list_item_view)

        # qvb_activities.addWidget(qlist_activities)
        # qvb_activities.setStretchFactor(qlist_activities, 1)
        self.qlist_activities.setFrameShape(QListWidget.Shape.Box)
        self.qlist_activities.setFrameShadow(QListWidget.Shadow.Plain)
        qvl_parent.addWidget(self.qlist_activities)
        qvl_parent.setStretchFactor(self.qlist_activities, 1)
        # endregion : Activity Listing

        btn_add_activity = QPushButton(icon=QIcon(f'{self.asset_dir}/icons/add.png'), text='Add New Activity')
        btn_add_activity.setFixedHeight(54)
        btn_add_activity.clicked.connect(self.add_activity)
        btn_add_activity.setStyleSheet(big_action_button_style())
        qvl_parent.addWidget(btn_add_activity)
        qvl_parent.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(qvl_parent)
        self.setStyleSheet("color: black;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor("#CCDDFF"))  # Set border color
        painter.drawRect(self.rect())  # Draw border around the widget

    def save_experiment(self):
        # TODO Save self.experiment into  ../data/data.json file
        print("TODO Convert self.experiment into JSON & Save into the ../data/data.json file")

    def update_activity_in_expt(self, activity):
        for i, a in enumerate(self.experiment.activities):
            if a.id == activity.id:
                self.experiment.activities[i] = activity
        self.save_experiment()

    def activity_item_deleted(self, act, serial):
        new_acts = []
        for a in self.experiment.activities:
            if a.id == act.id:
                continue
            new_acts.append(a)
        self.qlist_activities.takeItem(serial - 1)
        self.experiment.activities = new_acts
        self.save_experiment()

    def expt_name_changed(self, new_text):
        now = time.time()
        if now - self.title_change_ems < 500:
            return
        self.title_change_ems = now
        self.experiment.name = new_text
        self.save_experiment()

    def delete_expt(self):
        # TODO Delete experiment
        show_under_construction_message(self.asset_dir)

    def transition_secs_subtract_clicked(self):
        if self.experiment.transition_secs <= 5:
            return
        self.experiment.transition_secs -= 1
        self.qlb_tr_secs.setText(str(self.experiment.transition_secs))
        self.save_experiment()

    def transition_secs_add_clicked(self):
        self.experiment.transition_secs += 1
        self.qlb_tr_secs.setText(str(self.experiment.transition_secs))
        self.save_experiment()

    def reps_subtract_clicked(self):
        if self.experiment.reps_per_activity <= 1:
            return
        self.experiment.reps_per_activity -= 1
        self.qlb_reps.setText(str(self.experiment.reps_per_activity))
        self.save_experiment()

    def reps_add_clicked(self):
        self.experiment.reps_per_activity += 1
        self.qlb_reps.setText(str(self.experiment.reps_per_activity))
        self.save_experiment()

    def add_activity(self):
        # TODO Add activity UI with default texts, let it be edited, save into the expt. model
        show_under_construction_message(self.asset_dir)

    def start_expt_session(self):
        new_name, ok = QInputDialog.getText(self, 'New Experiment Session', 'Enter Session/Participant Name:')
        if ok:
            api.reset_for_new_session(new_name)
            window = SessionWindow(self.experiment, new_name, asset_dir=self.asset_dir)
            window.showMaximized()
            window.show()
