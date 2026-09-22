from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal


class Navbar(QWidget):
    logout_clicked = pyqtSignal()

    def __init__(self, user_name="User"):
        super().__init__()
        self.user_name = user_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        title = QLabel(f"FIVORA — Welcome, {self.user_name}")
        title.setStyleSheet('font-weight: bold;')

        spacer = QLabel()
        spacer.setSizePolicy(title.sizePolicy())

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedHeight(28)
        logout_btn.clicked.connect(self.logout_clicked.emit)

        layout.addWidget(title)
        layout.addWidget(spacer)
        layout.addWidget(logout_btn)

        self.setLayout(layout)
