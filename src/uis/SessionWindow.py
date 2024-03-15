import random
from enum import Enum
from math import ceil
from sys import stderr

from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QHBoxLayout, QPushButton, \
    QDesktopWidget

from src.helpers import icon_only_button_style, progressbar_style, api
from src.models.Activity import Activity

STR_NONE = 'none'
TR_ACTIVITY = Activity(100, "Be steady please ...",
                       20, 0, "", "")


def get_img(path):
    lbl = QLabel()
    img = QPixmap(path)
    lbl.setPixmap(img)
    lbl.setScaledContents(True)
    lbl.setMaximumWidth(300)
    lbl.setMaximumHeight(270)
    return lbl


class SessionStates(Enum):
    STARTING = 0
    IMG_1 = 1
    IMG_2 = 2
    TRANSITION = 3
    PAUSED = 4
    ENDED = 5


class SessionWindow(QMainWindow):
    def __init__(self, experiment, session_name, asset_dir):
        super().__init__()
        self.setWindowTitle(experiment.name)
        self.setWindowIcon(QIcon(f"{asset_dir}/icons/app_icon.png"))
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowFullScreen)
        screen_geometry = QDesktopWidget().screenGeometry()
        # screen_geometry.setY(screen_geometry.y()-80)
        self.setGeometry(screen_geometry)
        self.showFullScreen()

        self.experiment = experiment
        self.asset_dir = asset_dir

        self.curr_state = SessionStates.STARTING
        self.state_before_paused = self.curr_state
        self.curr_rep_no = 1
        self.curr_activity = TR_ACTIVITY
        self.curr_activity_dur_secs = self.get_curr_activity_duration()
        self.last_activity_id = -1
        self.countdown = self.experiment.transition_secs  # `self.countdown` should be decremented by 0.5s, as the timer expires every 500ms

        self.start_mp_sound = QMediaPlayer()
        self.start_mp_sound.setMedia(
            QMediaContent(QUrl.fromLocalFile(f"{self.asset_dir}/sounds/stop_4secs.mp3")))  # start_4secs
        self.start_mp_sound.stateChanged.connect(lambda: self.start_sound_ended)
        self.start_mp_sound.error.connect(self.media_error)
        self.stop_mp_sound = QMediaPlayer()
        self.stop_mp_sound.setMedia(QMediaContent(QUrl.fromLocalFile(f"{self.asset_dir}/sounds/stop_4secs.mp3")))
        self.stop_mp_sound.stateChanged.connect(lambda: self.stop_sound_ended)
        self.stop_mp_sound.error.connect(self.media_error)

        self.qvl_parent = QVBoxLayout()
        self.qvl_parent.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        qhb_menu_bar = QHBoxLayout()
        btn_close = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/close.png"))
        btn_close.setIconSize(QSize(32, 32))
        btn_close.setFixedSize(48, 48)
        btn_close.clicked.connect(self.close_clicked)
        btn_close.setStyleSheet(icon_only_button_style())
        qhb_menu_bar.addWidget(btn_close)
        qlb_dummy_bottom = QLabel()
        qhb_menu_bar.addWidget(qlb_dummy_bottom)
        qhb_menu_bar.setStretchFactor(qlb_dummy_bottom, 1)
        self.btn_pause = QPushButton(icon=QIcon(f"{self.asset_dir}/icons/pause.png"))
        self.btn_pause.setIconSize(QSize(24, 24))
        self.btn_pause.setFixedSize(48, 48)
        self.btn_pause.clicked.connect(self.pause_clicked)
        self.btn_pause.setStyleSheet(icon_only_button_style())
        qhb_menu_bar.addWidget(self.btn_pause)
        self.qvl_parent.addLayout(qhb_menu_bar)

        self.qlb_session = QLabel(f"Session/Participant: {session_name}")
        self.qlb_session.setFont(QFont('Courier', 14, 900, False))
        self.qlb_session.setStyleSheet('padding: 8px; color:red')
        self.qvl_parent.addWidget(self.qlb_session, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_rep_no = QLabel(self.get_rep_count_text())
        self.qlb_rep_no.setFont(QFont('Courier', 18, 600, False))
        self.qlb_rep_no.setStyleSheet('padding: 8px;')
        self.qvl_parent.addWidget(self.qlb_rep_no, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_img = get_img(f'{self.asset_dir}/expt/dish_mv_rg1.png')
        self.qlb_img.setVisible(False)
        self.qvl_parent.addWidget(self.qlb_img, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_wait_time = QLabel(f"{self.countdown}")
        self.qlb_wait_time.setFont(QFont('Courier', 84, 800, False))
        self.qlb_wait_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qlb_wait_time.setMinimumSize(self.qlb_img.size())
        self.qlb_wait_time.setStyleSheet('padding: 16px;')
        self.qvl_parent.addWidget(self.qlb_wait_time, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qpb_action_time = QProgressBar()
        self.qpb_action_time.setTextVisible(False)
        self.qpb_action_time.setMinimumSize(600, 16)
        self.qpb_action_time.setMaximumSize(800, 24)
        self.qpb_action_time.setMaximum(100)
        self.qpb_action_time.setValue(35)
        self.qpb_action_time.setStyleSheet(progressbar_style())
        self.qvl_parent.addWidget(self.qpb_action_time, alignment=Qt.AlignmentFlag.AlignCenter)

        self.qlb_activity_name = QLabel(f"Current Activity: {self.curr_activity.name}")
        self.qlb_activity_name.setFont(QFont('Courier', 16, 600, False))
        self.qlb_activity_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.qlb_activity_name.setStyleSheet('padding: 8px;')
        self.qvl_parent.addWidget(self.qlb_activity_name, alignment=Qt.AlignmentFlag.AlignCenter)
        # self.qvl_parent.addStretch()

        self.imgUpdateTimer = QTimer(self)
        self.imgUpdateTimer.setInterval(500)  # .5 seconds
        self.imgUpdateTimer.timeout.connect(lambda: self.handle_state_500ms())
        self.imgUpdateTimer.start()

        widget = QWidget()
        widget.setStyleSheet("background-color: white; color: black;")
        widget.setLayout(self.qvl_parent)
        self.setCentralWidget(widget)

    def get_curr_activity_duration(self):
        return self.curr_activity.duration_secs + random.randint(
            -self.curr_activity.duration_randomness, self.curr_activity.duration_randomness)

    def get_rep_count_text(self):
        c = 0
        for i, a in enumerate(self.experiment.activities):
            if a.id == self.curr_activity.id:
                c = i + 1
                break
        _x = min(self.curr_rep_no, self.experiment.reps_per_activity)
        return f"Repetition: {_x}/{self.experiment.reps_per_activity}, Activity: {c if c > 0 else '--'}/{len(self.experiment.activities)}"

    def close_clicked(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint & ~Qt.FramelessWindowHint)
        self.showNormal()
        self.setGeometry(100, 100, 600, 400)
        # Post 'none' annotation before closing
        api.post_next_action_label(STR_NONE)
        self.stop_all_sounds()
        # self.close() <-- Instead of directly calling, we're giving the OS a little bit of delay to dispose the resources first
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
            if self.countdown == 3.5:
                # Play start sound
                self.start_mp_sound.play()
            if self.countdown <= 0:
                self.curr_state = SessionStates.IMG_1
            self.qpb_action_time.setValue(int(self.countdown * 100 / self.experiment.transition_secs))

        elif self.curr_state == SessionStates.IMG_1 or self.curr_state == SessionStates.IMG_2:
            if self.countdown == 3.5:
                # Play stop sound
                self.stop_mp_sound.play()
            self.handle_activity_session()
            self.qpb_action_time.setValue(int(self.countdown * 100 / self.curr_activity_dur_secs))

        elif self.curr_state == SessionStates.PAUSED:
            self.countdown += 0.5

        elif self.curr_state == SessionStates.ENDED:
            self.stop_all_sounds()
            if self.countdown <= 0:
                self.close_clicked()
        else:
            stderr.write(f"Undefined SessionState: {self.curr_state}")
        if self.curr_rep_no > self.experiment.reps_per_activity:
            self.qlb_img.setVisible(False)
            self.qlb_wait_time.setVisible(True)
            self.qlb_wait_time.setText("Completed!")
            self.curr_state = SessionStates.ENDED
            self.curr_activity = Activity(-101, "All are done!", 0, 0, "", "")
            self.curr_rep_no = self.experiment.reps_per_activity
            self.countdown = 5
        next_act_str = f"\nNext: {self.pick_next_activity().name}" if self.curr_activity.id == TR_ACTIVITY.id else ""
        self.qlb_activity_name.setText(f"Current Activity: {self.curr_activity.name}{next_act_str}")

    def handle_activity_session(self):
        is_img1 = self.curr_state == SessionStates.IMG_1
        self.qlb_rep_no.setText(self.get_rep_count_text())
        if self.curr_activity.id == TR_ACTIVITY.id:
            self.curr_activity = self.pick_next_activity()
            self.curr_activity_dur_secs = self.get_curr_activity_duration()
            self.countdown = self.curr_activity_dur_secs
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
            self.curr_activity_dur_secs = self.get_curr_activity_duration()
            api.post_next_action_label(self.curr_activity.name if self.curr_activity.id != TR_ACTIVITY.id else STR_NONE)
            # Check completion? <-- For now, let's have a static session at the end of the session

    def start_sound_ended(self):
        if self.start_mp_sound.state() == QMediaPlayer.EndOfMedia:
            self.start_mp_sound.stop()

    def stop_sound_ended(self):
        if self.stop_mp_sound.state() == QMediaPlayer.EndOfMedia:
            self.stop_mp_sound.stop()

    def pick_next_activity(self):
        if self.last_activity_id == -1:  # initial round
            return self.experiment.activities[0]
        for i, a in enumerate(self.experiment.activities):
            if a.id == self.last_activity_id:
                idx = (i + 1) % len(self.experiment.activities)
                if idx < i:  # or, idx == 0 ?
                    self.curr_rep_no += 1
                return self.experiment.activities[idx]
        return TR_ACTIVITY

    def stop_all_sounds(self):
        if self.start_mp_sound.state() == QMediaPlayer.PlayingState:
            self.start_mp_sound.stop()
        if self.stop_mp_sound.state() == QMediaPlayer.PlayingState:
            self.stop_mp_sound.stop()

    # noinspection PyMethodMayBeStatic
    def media_error(self, error):
        print("Media player error:", error)

    def closeEvent(self, event):
        try:
            self.imgUpdateTimer.stop()
            self.imgUpdateTimer.deleteLater()
            self.stop_all_sounds()
        except Exception as e:
            print("QTimer deletion error on window close:", e)
        event.accept()
