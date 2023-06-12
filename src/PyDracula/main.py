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

if __name__ != "__main__":
    script_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(script_path)

from dracula_modules import *
from widgets import *

# Remove [import resources_rc] in ui_main.py!!

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        self.ui.textBrowser.setOpenExternalLinks(True)

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
        self.load_chatlog_info()
        self.load_character_info()

    def load_character_info(self):
        from voice_translator import load_tts_setting
        # Todo: clean return vars
        character_name, tts_character_name, tts_language, voice_id, voice_volume, USE_D_BOT = load_tts_setting()

        from LangAIComm import get_character_info
        your_name, bot_name, greeting, context, bot_image = get_character_info(character_name)

        widgets.textEdit_yourname.setText(your_name)
        widgets.label_char_name.setText(bot_name)

        if bot_image is not None:
            # bot_pixmap = QPixmap.fromImage(bot_image)
            widgets.label_char_img.setPixmap(QPixmap(bot_image))

        widgets.textEdit_greeting.setText(greeting)
        widgets.textEdit_context.setText(context)

    def load_chatlog_info(self):
        from voice_translator import load_tts_setting
        # Todo: clean return vars
        character_name, tts_character_name, tts_language, voice_id, voice_volume, USE_D_BOT = load_tts_setting()

        print(f"charname {character_name}")
        from LangAIComm import get_chatlog_info
        chatlog_txt = get_chatlog_info(character_name)
        print(f"chatlog {chatlog_txt}")

        widgets.textEdit_chat_log.setText(chatlog_txt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
