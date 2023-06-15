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
import random

from PySide6.QtCore import QTimer
# IMPORT / GUI, SETTINGS AND WIDGETS
# ///////////////////////////////////////////////////////////////
# Packages
# from app.packages.widgets import * # Widgets

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# GUI
from dracula_modules.ui_page_messages import Ui_chat_page  # MainWindow
from dracula_modules.message import Message  # MainWindow


# MAIN WINDOW
# ///////////////////////////////////////////////////////////////
class Chat(QWidget):
    def __init__(
            self,
            char_dict
    ):
        QWidget.__init__(self)

        self.scroll_bar = None
        self.page = Ui_chat_page()
        self.page.setupUi(self)

        self.char_info_dict = char_dict   # for chat log

        bot_name = self.char_info_dict["character_name"]
        bot_description = self.char_info_dict["character_description"]
        bot_image = self.char_info_dict["character_image"]

        ## ADDED
        ###########################################################################

        try:
            if bot_image is not None:
                # Load original profile image & set output path
                original_image = QImage(os.path.normpath(bot_image))
                image_directory = os.path.dirname(os.path.normpath(bot_image))
                output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'chatlog', 'user')
                output_image_path = os.path.join(output_path, "profile_image_squared.png")
                # print(os.path.normpath(user_image))
                # print(output_image_path)

                # Determine the shorter side and longer side
                width = original_image.width()
                height = original_image.height()
                shorter_side = min(width, height)
                longer_side = max(width, height)

                # Calculate the coordinates for cropping
                margin = float(longer_side - shorter_side) / 2.0

                # TODO: test square image & width's longer iamge
                if width > height:
                    x = margin
                    y = 0
                else:
                    x = 0
                    y = margin

                # Create a square image by cropping the shorter side
                square_image = original_image.copy(x, y, shorter_side, shorter_side)

                # Resize the square image to 40x40 pixels
                resized_image = square_image.scaled(40, 40)

                # Save resized image to png
                resized_image.save(output_image_path)

                # UPDATE INFO
                self.page.user_image.setStyleSheet("#user_image { background-image: url(\"" + output_image_path.replace("\\", "/") + "\") }")
                # self.page.user_image.setPixmap(QPixmap(resized_image))
                ###########################################################################
                ## ADDED
            else:
                raise Exception('no bot profile image set')
        except Exception as e:
            print("[GUI] ERROR: ", e)

        self.page.user_name.setText(bot_name)
        self.page.user_description.setText(bot_description)

        # CHANGE PLACEHOLDER TEXT
        format_user_name = bot_name.replace(" ", "_").replace("-", "_")
        format_user_name = format_user_name.lower()
        self.page.line_edit_message.setPlaceholderText(f"Message #{str(format_user_name).lower()}")

        # ENTER / RETURN PRESSED
        self.page.line_edit_message.keyReleaseEvent = self.enter_return_release

        # ENTER / RETURN PRESSED
        self.page.btn_send_message.clicked.connect(self.send_message_entry)

        # LOAD CHAT LOG
        self.load_chat_log()

    # ENTER / RETURN SEND MESSAGE
    def enter_return_release(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message_entry()

    # SEND MESSAGE
    def send_message(self, text):
        self.message = Message(text, True)
        self.page.chat_messages_layout.addWidget(self.message, Qt.AlignCenter, Qt.AlignBottom)
        self.page.line_edit_message.setText("")

    # Send From Entry TextEdit
    def send_message_entry(self):
        if self.page.line_edit_message.text() != "":
            self.message = Message(self.page.line_edit_message.text(), True)
            self.page.chat_messages_layout.addWidget(self.message, Qt.AlignCenter, Qt.AlignBottom)
            self.page.line_edit_message.setText("")

            # SCROLL TO END
            QTimer.singleShot(10, lambda: self.page.messages_frame.setFixedHeight(
                self.page.chat_messages_layout.sizeHint().height()))
            QTimer.singleShot(15, lambda: self.scroll_to_end())

    # SEND MESSAGE BY FRIEND
    def send_by_friend(self, text):
        self.message = Message(text, False)
        self.page.chat_messages_layout.addWidget(self.message, Qt.AlignCenter, Qt.AlignBottom)
        self.page.line_edit_message.setText("")

    def load_chat_log(self):
        chat_log_str = self.char_info_dict["chat_log"]
        lines = chat_log_str.strip().splitlines()
        char_name = self.char_info_dict["character_name"]
        your_name = self.char_info_dict["your_name"]

        for line in lines:
            prefix = line.split(":")[0].strip()
            line = line.split(":")[1].strip()

            if prefix == char_name:
                # print(f"Bot said: {line}")
                self.send_by_friend(line)
            elif prefix == your_name:
                # print(f"You said: {line}")
                self.send_message(line)
            else:   # Other character    # TODO: when other character spoken, display name & other profile_image
                # print(f"{prefix} said: {line}")
                self.send_by_friend(line)

        try:
            print(
                self.page.messages_frame.setFixedHeight(
                    self.page.chat_messages_layout.sizeHint().height()))
            # SCROLL TO END
            QTimer.singleShot(10, lambda: self.page.messages_frame.setFixedHeight(
                self.page.chat_messages_layout.sizeHint().height()))
            QTimer.singleShot(15, lambda: self.scroll_to_end())
        except Exception as e:
            print("[GUI] ERROR: ", e)

    def scroll_to_end(self):
        # SCROLL TO END
        if self.scroll_bar:
            self.scroll_bar = self.page.chat_messages.verticalScrollBar()
            self.scroll_bar.setValue(self.scroll_bar.maximum())

