from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


def get_img(path):
    lbl = QLabel()
    img = QPixmap(path)
    lbl.setPixmap(img)
    lbl.setScaledContents(True)
    lbl.setMaximumWidth(500)
    lbl.setMaximumHeight(450)
    return lbl


class SessionWindow(QMainWindow):
    def __init__(self, asset_dir):
        super().__init__()
        self.setWindowTitle("CSI Annotator")
        self.asset_dir = asset_dir
        # setting geometry
        self.setGeometry(100, 100, 600, 400)
        # self.setFixedWidth(800)
        # self.setFixedHeight(600)
        self.img_no = 0

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img = get_img(f'{self.asset_dir}/dish_mv_rg1.png')
        self.layout.addWidget(self.lbl_img)

        self.imgUpdateTimer = QTimer(self)
        self.imgUpdateTimer.setInterval(500)  # .5 seconds
        self.imgUpdateTimer.timeout.connect(lambda: self.toggle_img())
        self.imgUpdateTimer.start()

        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def toggle_img(self):
        self.img_no = (self.img_no+1) % 2
        path = f'{self.asset_dir}/dish_mv_rg{self.img_no}.png'
        self.layout.removeWidget(self.lbl_img)
        self.lbl_img = get_img(path)
        self.layout.addWidget(self.lbl_img)
