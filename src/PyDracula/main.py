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

import sys
import os
import platform

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from PySide6.QtWidgets import *
from PySide6 import QtCore
from PySide6.QtCore import Qt

# IF MAIN THREAD IS THIS, APPEND SYS ENV PATH
if __name__ != "__main__":
    script_path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.dirname(script_path)  # able to import modules in src folder
    sys.path.append(script_path)
    sys.path.append(root_path)

from dracula_modules import *
from widgets import *

# CHATLOAD
from dracula_modules.page_messages import Chat # Chat Widget

# Remove [import resources_rc] in ui_main.py!!

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET CUSTOM VARIABLES
        # ///////////////////////////////////////////////////////////////
        self.char_info_dict : dict = None
        # [your_name, character_name, character_description, character_image, greeting, context, chat_log]

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        widgets.textBrowser.setOpenExternalLinks(True)

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Blessing AI"
        description = "Blessing AI"
        self.ui.titleLeftDescription.setText("AI Chat Interface")
        self.ui.titleLeftApp.setText("Blessing AI")
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        widgets.btn_share.clicked.connect(self.buttonClick)

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_mic_setting.clicked.connect(self.buttonClick)
        widgets.btn_character.clicked.connect(self.buttonClick)
        widgets.btn_tts_setting.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.Home_Page)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

        self.load_all_info()

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        global widgets
        if widgets is None:
            widgets = self.ui

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.Home_Page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

            self.chat_layout_update(self.char_info_dict)

        # SHOW CHARACTER PAGE
        if btnName == "btn_character":
            widgets.stackedWidget.setCurrentWidget(widgets.Character_page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        # SHOW MIC PAGE
        if btnName == "btn_mic_setting":
            widgets.stackedWidget.setCurrentWidget(widgets.Mic_Page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW TTS PAGE
        if btnName == "btn_tts_setting":
            widgets.stackedWidget.setCurrentWidget(widgets.TTS_Page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        if btnName == "btn_share":
            import webbrowser

            webbrowser.open('https://github.com/HWcomss/Blessing-AI')  # Go to Github Page
            print("Link BTN Clicked!")

        if btnName == "btn_exit":
            print("Exit BTN Clicked!")
            QtCore.QCoreApplication.instance().quit()

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # [GUI] LOAD CHAT
    # ///////////////////////////////////////////////////////////////
    def chat_layout_update(self, character_info):
        global widgets
        self.char_info_dict["character_description"] = "AI-Bot"

        # if btn.objectName():
        # REMOVE CHAT
        for chat in reversed(range(self.ui.chat_layout.count())):
            widgets.chat_layout.itemAt(chat).widget().deleteLater()
        self.chat = None

        # SET CHAT WIDGET
        self.chat = Chat(self.char_info_dict)
        # self.chat = Chat(btn.user_image, btn.user_name, btn.user_description, btn.objectName(), self.top_user.user_name)

        # ADD WIDGET TO LAYOUT
        widgets.chat_layout.addWidget(self.chat)

        # JUMP TO CHAT PAGE
        # widgets.app_pages.setCurrentWidget(widgets.chat)

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    # LOAD INFO EVENTS
    # ///////////////////////////////////////////////////////////////
    def load_all_info(self):
        self.load_character_info()
        self.load_chatlog_info()
        self.load_mic_info()

        self.chat_layout_update(self.char_info_dict)

    def load_character_info(self):
        global widgets
        from setting_info import SettingInfo    # noqa
        settings_json = SettingInfo.load_settings()

        from LangAIComm import get_character_info   # noqa
        char_dict = get_character_info(settings_json["character_name"])
        # print(char_dict)

        widgets.textEdit_yourname.setText(char_dict["your_name"])
        widgets.label_char_name.setText(char_dict["character_name"])

        bot_image = char_dict["character_image"] # TODO: check None, if there's no image

        if bot_image is not None:
            # bot_pixmap = QPixmap.fromImage(bot_image)
            widgets.label_char_img.setPixmap(QPixmap(bot_image))

        widgets.textEdit_greeting.setText(char_dict["greeting"])
        widgets.textEdit_context.setText(char_dict["context"])

        self.char_info_dict = char_dict

    def load_chatlog_info(self):
        global widgets

        if self.char_info_dict is None:
            print("[GUI] : Chat info dict is None, now loading character info...")
            self.load_character_info()

        from setting_info import SettingInfo    # noqa

        settings_json = SettingInfo.load_settings()
        character_name = settings_json["character_name"]
        # print(f"charname: {character_name}")

        from LangAIComm import get_chatlog_info # noqa

        chatlog_txt = get_chatlog_info(character_name)
        # print(f"chatlog: {chatlog_txt}")
        self.char_info_dict["chat_log"] = chatlog_txt

        # widgets.listView_chat_log.addItem(chatlog_txt)
        # widgets.textEdit_chat_log.setText(chatlog_txt)

        ## Get Last 2 messages
        messages = chatlog_txt.split("\n")

        last_user_message = messages[-2]
        last_bot_reply = messages[-1]

        # Remove name
        import re
        last_user_message = processed_message = re.sub(r"^[^:]+:\s*", "", last_user_message, count=1)
        last_bot_reply = processed_message = re.sub(r"^[^:]+:\s*", "", last_bot_reply, count=1)

        # Remove index 0 blank
        if last_user_message[0] == " ":
            last_user_message = last_user_message[1:]

        if last_bot_reply[0] == " ":
            last_bot_reply = last_bot_reply[1:]

        widgets.textEdit_user_message.setText(last_user_message)
        widgets.textEdit_bot_reply.setText(last_bot_reply)

    @staticmethod
    def load_mic_info():
        print()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
