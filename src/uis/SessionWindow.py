from enum import Enum
from math import ceil
from sys import stderr

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QHBoxLayout, QPushButton

from src.helpers import icon_only_button_style, progressbar_style, api
from src.models.Activity import Activity

STR_NONE = 'none'
TR_ACTIVITY = Activity(100, "Keep steady please! Waiting to start ...", 20, "", "")


def get_img(path):
    lbl = QLabel()
    img = QPixmap(path)
    lbl.setPixmap(img)
    lbl.setScaledContents(True)
    lbl.setMaximumWidth(500)
    lbl.setMaximumHeight(450)
    return lbl


class SessionStates(Enum):
    STARTING = 0
    IMG_1 = 1
    IMG_2 = 2
    TRANSITION = 3
    PAUSED = 4


class SessionWindow(QMainWindow):
    def __init__(self, experiment, session_name, asset_dir):
        super().__init__()
        self.setWindowTitle(experiment.name)
        self.experiment = experiment
        self.asset_dir = asset_dir

        self.curr_state = SessionStates.STARTING
        self.state_before_paused = self.curr_state
        self.curr_rep_no = 1
        self.curr_activity = TR_ACTIVITY
        self.last_activity_id = -1
        self.countdown = self.experiment.transition_secs  # `self.countdown` should be decremented by 0.5s, as the timer expires every 500ms

        self.qvl_parent = QVBoxLayout()
        self.qvl_parent.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.qlb_session = QLabel(f"Session/Participant: {session_name}")
        self.qlb_session.setFont(QFont('Courier', 18, 900, False))
        self.qlb_session.setStyleSheet('padding: 24px; color:red')
        self.qvl_parent.addWidget(self.qlb_session, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_rep_no = QLabel(f"Repetition: {self.curr_rep_no}/{self.experiment.reps_per_activity}")
        self.qlb_rep_no.setFont(QFont('Courier', 24, 600, False))
        self.qlb_rep_no.setStyleSheet('padding: 24px;')
        self.qvl_parent.addWidget(self.qlb_rep_no, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_wait_time = QLabel(f"{self.countdown}")
        self.qlb_wait_time.setFont(QFont('Courier', 96, 800, False))
        self.qlb_wait_time.setStyleSheet('padding: 48px;')
        self.qvl_parent.addWidget(self.qlb_wait_time, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_img = get_img(f'{self.asset_dir}/expt/dish_mv_rg1.png')
        self.qlb_img.setVisible(False)
        self.qvl_parent.addWidget(self.qlb_img, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qpb_action_time = QProgressBar()
        self.qpb_action_time.setTextVisible(False)
        self.qpb_action_time.setMinimumSize(600, 32)
        self.qpb_action_time.setMaximumSize(800, 48)
        self.qpb_action_time.setMaximum(100)
        self.qpb_action_time.setValue(35)
        self.qpb_action_time.setStyleSheet(progressbar_style())
        self.qvl_parent.addWidget(self.qpb_action_time, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_activity_name = QLabel(f"Current Activity: {self.curr_activity.name}")
        self.qlb_activity_name.setFont(QFont('Courier', 20, 600, False))
        self.qlb_activity_name.setStyleSheet('padding: 24px;')
        self.qvl_parent.addWidget(self.qlb_activity_name, alignment=Qt.AlignmentFlag.AlignCenter)
        self.qvl_parent.addStretch()

        qhb_bottom_bar = QHBoxLayout()
        btn_close = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/close.png"))
        btn_close.setIconSize(QSize(32, 32))
        btn_close.setFixedSize(64, 64)
        btn_close.clicked.connect(self.close_clicked)
        btn_close.setStyleSheet(icon_only_button_style())
        qhb_bottom_bar.addWidget(btn_close)
        qlb_dummy_bottom = QLabel()
        qhb_bottom_bar.addWidget(qlb_dummy_bottom)
        qhb_bottom_bar.setStretchFactor(qlb_dummy_bottom, 1)
        self.btn_pause = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/pause.png"))
        self.btn_pause.setIconSize(QSize(32, 32))
        self.btn_pause.setFixedSize(64, 64)
        self.btn_pause.clicked.connect(self.pause_clicked)
        self.btn_pause.setStyleSheet(icon_only_button_style())
        qhb_bottom_bar.addWidget(self.btn_pause)
        self.qvl_parent.addLayout(qhb_bottom_bar)

        self.imgUpdateTimer = QTimer(self)
        self.imgUpdateTimer.setInterval(500)  # .5 seconds
        self.imgUpdateTimer.timeout.connect(lambda: self.handle_state_500ms())
        self.imgUpdateTimer.start()

        widget = QWidget()
        widget.setStyleSheet("background-color: white; color: black;")
        widget.setLayout(self.qvl_parent)
        self.setCentralWidget(widget)

    def close_clicked(self):
        # Post 'none' annotation before closing
        api.post_next_action_label(STR_NONE)
        self.close()

    def pause_clicked(self):
        if self.curr_state != SessionStates.PAUSED:
            api.post_next_action_label(STR_NONE)
            self.state_before_paused = self.curr_state
            self.curr_state = SessionStates.PAUSED
            self.btn_pause.setIcon(QIcon(f"{self.asset_dir}/icons/play.png"))
        else:
            api.post_next_action_label(self.curr_activity.name if self.curr_activity.id != TR_ACTIVITY.id else STR_NONE)
            self.curr_state = self.state_before_paused
            self.btn_pause.setIcon(QIcon(f"{self.asset_dir}/icons/pause.png"))
        # The rest of the effects would be handled on the next timer event (after 0.5s)

    def handle_state_500ms(self):
        self.countdown -= 0.5

        if self.curr_state == SessionStates.STARTING or self.curr_state == SessionStates.TRANSITION:
            self.qlb_wait_time.setText(f"{int(ceil(self.countdown))}")
            if self.countdown <= 0:
                self.curr_state = SessionStates.IMG_1
            self.qpb_action_time.setValue(int(self.countdown * 100 / self.experiment.transition_secs))

        elif self.curr_state == SessionStates.IMG_1 or self.curr_state == SessionStates.IMG_2:
            self.handle_activity_session()
            self.qpb_action_time.setValue(int(self.countdown * 100 / self.curr_activity.duration_secs))

        elif self.curr_state == SessionStates.PAUSED:
            self.countdown += 0.5
        else:
            stderr.write(f"Undefined SessionState: {self.curr_state}")
        if self.curr_rep_no > self.experiment.reps_per_activity:
            self.qlb_img.setVisible(False)
            self.qlb_wait_time.setVisible(True)
            self.qlb_wait_time.setText("Completed!")
        self.qlb_activity_name.setText(f"Current Activity: {self.curr_activity.name}")

    def handle_activity_session(self):
        is_img1 = self.curr_state == SessionStates.IMG_1
        if self.curr_activity.id == TR_ACTIVITY.id:
            self.curr_activity = self.pick_next_activity()
            self.countdown = self.curr_activity.duration_secs
            api.post_next_action_label(self.curr_activity.name if self.curr_activity.id != TR_ACTIVITY.id else STR_NONE)
        if not self.qlb_img.isVisible():
            self.qlb_img.setVisible(True)
            self.qlb_wait_time.setVisible(False)
        path = (f'{self.asset_dir}/expt/' +
                f'{self.curr_activity.img1 if is_img1 else self.curr_activity.img2}')
        self.qlb_img.setPixmap(QPixmap(path))
        if self.countdown > 0:
            self.curr_state = SessionStates.IMG_2 if is_img1 else SessionStates.IMG_1
        else:
            self.qlb_img.setVisible(False)
            self.qlb_wait_time.setVisible(True)
            self.curr_state = SessionStates.TRANSITION
            self.countdown = self.experiment.transition_secs
            self.last_activity_id = self.curr_activity.id
            self.curr_activity = TR_ACTIVITY
            api.post_next_action_label(self.curr_activity.name if self.curr_activity.id != TR_ACTIVITY.id else STR_NONE)

    def pick_next_activity(self):
        if self.last_activity_id == -1:
            return self.experiment.activities[0]
        for i, a in enumerate(self.experiment.activities):
            if a.id == self.last_activity_id:
                idx = (i + 1) % len(self.experiment.activities)
                if idx < i:
                    self.curr_rep_no += 1
                    self.qlb_rep_no.setText(f"Repetition: {self.curr_rep_no}/{self.experiment.reps_per_activity}")
                return self.experiment.activities[idx]
        return TR_ACTIVITY

    # TODO Add close-event to post `none` label
