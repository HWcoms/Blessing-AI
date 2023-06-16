# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

# DEFAULT PACKAGES
# ///////////////////////////////////////////////////////////////
import os

# IMPORT / GUI, SETTINGS AND WIDGETS
# ///////////////////////////////////////////////////////////////
# Packages
from datetime import datetime

# from app.packages.pyside_or_pyqt import * # Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# GLOBALS
send_by = None
btn_image = None

# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class Message(QWidget):
    def __init__(self, message, me_send, pf_image=None):
        QWidget.__init__(self)
        global send_by  # user, bot, other
        send_by = me_send

        global btn_image
        btn_image = pf_image

        if send_by != 'user' and send_by != 'bot' and send_by != 'other':
            print("[GUI] ERROR: Message(message, send_by) -> send_by argument is not supported")
            return

        self.setMinimumHeight(20)
        self.setup_ui()
        self.setFixedHeight(self.layout.sizeHint().height())

        from PySide6.QtWidgets import QSizePolicy, QLayout

        # ADDED
        # sp = self.sizePolicy()
        # sp.setHorizontalPolicy(QSizePolicy.Expanding)
        # self.setSizePolicy(sp)
        # ADDED

        # SET MESSAGE
        self.message.setText(message)

        # SET DATE TIME
        date_time = datetime.now()
        date_time_format = date_time.strftime("%m/%d/%Y %H:%M")
        self.data_message.setText(str(date_time_format))

        self.setStyleSheet("#bg {background-color: #FFFFFF;}")  # testing bg with white

    def setup_ui(self):
        # LAYOUT
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # FRAME BG
        # self.spacer = QVertical
        self.bg = QFrame()
        # self.bg.setFixedWidth(500)
        if send_by == 'user':
            self.bg.setStyleSheet(
                "#bg {background-color: #0e0e0f; border-radius: 10px; margin-left: 0; } #bg:hover { background-color: #252628; }")
        elif send_by == 'bot' or send_by == 'other':
            self.bg.setStyleSheet(
                "#bg {background-color: #28282b; border-radius: 10px; margin-right: 0; } #bg:hover { background-color: #252628; }")
        self.bg.setObjectName("bg")

        # FRAME BG
        self.btn = QPushButton()
        self.btn.setMinimumSize(40, 40)
        self.btn.setMaximumSize(40, 40)     # TODO: CHANGE BTN IMAGE TO PROFILE IMAGES
        if btn_image is None:
            print("no button image defined")
            self.btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border-radius: 20px;
                        background-repeat: no-repeat;
                        background-position: center;
                        background-image: url(:/chat/icons_svg/images/chatlog/icons_svg/icon_more_options.svg);
                    }
                    QPushButton:hover {
                        background-color: rgb(61, 62, 65);
                    }
                    QPushButton:pressed {
                        background-color: rgb(16, 17, 18);
                    }        
                    """)



        # LABEL MESSAGE
        self.message = QLabel()
        self.message.setText("message test")

        if send_by == 'user':
            self.message.setStyleSheet("""
            QLabel{
                background-color: #0e0e0f;
                border-radius: 10px;
                font: 500 11pt 'Segoe UI';
            }
            """)
        elif send_by == 'bot' or send_by == 'other':
            self.message.setStyleSheet("""
            QLabel{
                background-color: #28282b;
                border-radius: 10px;
                font: 500 11pt 'Segoe UI';
            }
            """)

        self.message.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        if send_by == 'user':
            # self.layout.addWidget(self.bg)
            self.layout.addWidget(self.message)
            self.layout.addWidget(self.btn)
        elif send_by == 'bot' or send_by == 'other':
            self.layout.addWidget(self.btn)
            # self.layout.addWidget(self.bg)
            self.layout.addWidget(self.message)

        # LAYOUT INSIDE
        self.layout_inside = QVBoxLayout(self.bg)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # LABEL MESSAGE 
        self.data_message = QLabel()
        self.data_message.setText("date")
        self.data_message.setStyleSheet("font: 8pt 'Segoe UI'; color: #4c5154")
        if send_by == 'user':
            self.data_message.setAlignment(Qt.AlignRight)
        elif send_by == 'bot' or send_by == 'other':
            self.data_message.setAlignment(Qt.AlignLeft)

        # self.layout_inside.addWidget(self.message)
        # self.layout_inside.addWidget(self.data_message)
