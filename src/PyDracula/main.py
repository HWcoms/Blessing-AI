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
        self.char_info_dict : dict = None   # [your_name, character_name,
                                            # character_description, character_image,
                                            # greeting, context]

        self.chat_info_dict : dict = None   # <- Contains Chatlog + other_settings.txt
                                            # [chatlog, chatlog_filename,
                                            # discord_bot, discord_print_language

        # TODO: create audio_setting, prompt setting (devcices)
        self.audio_info_dict: dict = None   # [mic_index, mic_threshold, phrase_timeout,

                                            # spk_index, tts_character_name, tts_language
                                            # voice_id, voice_speed, voice_volume,
                                            #  intonation_scale, pre_phoneme_length, post_phoneme_length]

        self.prompt_info_dict: dict = None  # [max_prompt_token, max_reply_token,
                                            # ai_model_language]
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        widgets.textBrowser.setOpenExternalLinks(True)
        self.chat = None
        self.last_scroll_value = -1
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
        widgets.btn_character.clicked.connect(self.buttonClick)
        widgets.btn_audio_setting.clicked.connect(self.buttonClick)
        widgets.btn_prompt_setting.clicked.connect(self.buttonClick)
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
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))   # set pink color to menu selector

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

            self.load_chatlog_info()

            self.last_scroll_value = self.chat.get_scroll_value()
            self.chat_layout_update(self.last_scroll_value)

        # SHOW CHARACTER PAGE
        if btnName == "btn_character":
            widgets.stackedWidget.setCurrentWidget(widgets.Character_page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.load_character_info()

        # SHOW MIC PAGE
        if btnName == "btn_prompt_setting":
            widgets.stackedWidget.setCurrentWidget(widgets.Mic_Page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

            self.load_prompt_info()

        # SHOW AUDIO PAGE
        if btnName == "btn_audio_setting":
            widgets.stackedWidget.setCurrentWidget(widgets.TTS_Page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.load_audio_info()

        if btnName == "btn_share":
            import webbrowser

            webbrowser.open('https://github.com/HWcomss/Blessing-AI')  # Go to Github Page
            print("Link BTN Clicked!")

        if btnName == "btn_exit":
            print("Exit BTN Clicked!")
            QtCore.QCoreApplication.instance().quit()

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # [GUI] DRAW CHAT
    # ///////////////////////////////////////////////////////////////
    def chat_layout_update(self, dest_scroll_value = -1):
        global widgets
        # self.char_info_dict["character_description"]
        # self.char_info_dict["character_description"] = "AI-Bot" # Character Description
        if self.last_scroll_value == dest_scroll_value and self.last_scroll_value != -1:
            print("\033[34m" + f"[main GUI.chat_layout_update]: scroll value is same! no need to scroll" + "\033[0m" )
            return

        if self.last_scroll_value == -1:
            self.last_scroll_value = 0
        elif self.chat:
                self.last_scroll_value = self.chat.get_scroll_value()
        else:
            print("\033[31m" + "Error [main GUI.chat_layout_update]: failed to load chat" + "\033[0m" )
            return 0

        # print(f"[main GUI.chat_layout_update]: last_scroll_value = {last_scroll_value}")

        # REMOVE CHAT
        for chat in reversed(range(self.ui.chat_layout.count())):
            widgets.chat_layout.itemAt(chat).widget().deleteLater()
        self.chat = None

        # SET CHAT WIDGET
        self.chat = Chat(self, self.char_info_dict, self.chat_info_dict)

        # ADD WIDGET TO LAYOUT
        widgets.chat_layout.addWidget(self.chat)

        # self.chat.set_scroll_value(last_scroll_value)
        self.chat.scroll_to_animation(last_value=self.last_scroll_value, value=dest_scroll_value)

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
        self.load_character_info()  # Load Character page
        self.load_chatlog_info()    # Load chatlog information

        self.chat_layout_update()    # Load Home Page

        self.load_audio_info()    # Load Audio page

        self.load_other_info()  # Load other information
        self.load_prompt_info() # Load prompt information


    def load_character_info(self):
        global widgets
        from setting_info import SettingInfo    # noqa
        char_settings_json = SettingInfo.load_character_settings()
        character_name = char_settings_json["character_name"]
        user_name = char_settings_json["your_name"]

        from LangAIComm import get_character_info   # noqa
        char_dict = get_character_info(character_name)  # Dict [your_name, character_name, greeting, context, character_image]
        # print(char_dict)

        bot_image = char_dict["character_image"] # TODO: check None, if there's no image

        if bot_image is not None:
            # bot_pixmap = QPixmap.fromImage(bot_image)
            widgets.label_char_img.setPixmap(QPixmap(bot_image))

        widgets.textEdit_greeting.setText(char_dict["greeting"])
        widgets.textEdit_context.setText(char_dict["context"])

        self.char_info_dict = char_dict

        # Force set 'char_name' and 'your_name' from 'Character_Settings.txt'
        self.char_info_dict.update(char_settings_json)
        # TODO: if your_name or character_name is changed in settings_txt, program don't know who is the user in chatlog_txt

        widgets.textEdit_yourname.setText(user_name)
        widgets.label_char_name.setText(character_name)

        # print(self.char_info_dict)


    def load_chatlog_info(self):
        global widgets

        if self.char_info_dict is None:
            print("[GUI] : Chat info dict is None, now loading character info...")
            self.load_character_info()

        if self.chat_info_dict is None:
            self.chat_info_dict = {}

        from setting_info import SettingInfo    # noqa

        char_settings_json = SettingInfo.load_character_settings()
        character_name = self.char_info_dict["character_name"]
        user_name = self.char_info_dict["your_name"]
        # print(f"charname: {character_name}")

        from LangAIComm import get_chatlog_info # noqa

        chatlog_txt = get_chatlog_info(character_name)
        # print(f"chatlog: {chatlog_txt}")
        self.chat_info_dict["chatlog"] = chatlog_txt

        # widgets.listView_chatlog.addItem(chatlog_txt)
        # widgets.textEdit_chatlog.setText(chatlog_txt)

        ## Get Last 2 messages
        messages = chatlog_txt.split("\n")

        last_user_message = ""
        last_bot_reply = ""
        count = 0

        if len(messages) >= 2:
            for message in reversed(messages):
                if (count >= 2):
                    break

                if message.startswith(f"{character_name}:"):
                    # last_bot_message = message.replace("Kato Megumi:", "").strip()
                    last_bot_reply = message
                    # print(last_bot_message)
                    count = count + 1
                    continue
                elif message.startswith(f"{user_name}:"):
                    # last_user_message = message.replace("coms:", "").strip()
                    last_user_message = message
                    # print(last_user_message)
                    count = count + 1
                    continue
        else:
            print("Not enough messages in the chat log.")

        widgets.textEdit_user_message.setText(last_user_message)
        widgets.textEdit_bot_reply.setText(last_bot_reply)

        # get chatlog filename
        self.chat_info_dict["chatlog_filename"] = SettingInfo.get_chatlog_filename(character_name)

    @staticmethod
    def load_mic_info():


        print()

    def load_audio_info(self):
        if self.audio_info_dict is None:
            self.audio_info_dict = {}

        from setting_info import SettingInfo  # noqa
        self.audio_info_dict.update(SettingInfo.load_audio_settings())

    def load_other_info(self):
        if self.chat_info_dict is None:
            self.chat_info_dict = {}

        from setting_info import SettingInfo  # noqa
        self.chat_info_dict.update(SettingInfo.load_other_settings())

    def load_prompt_info(self):
        if self.prompt_info_dict is None:
            self.prompt_info_dict = {}

        from setting_info import SettingInfo  # noqa
        self.prompt_info_dict.update(SettingInfo.load_prompt_settings())

    def after_generate_reply(self, success = 1):
        if success == -1:
            self.last_scroll_value = self.chat.get_scroll_value()
            self.chat.scroll_to_animation(last_value=self.last_scroll_value)
            self.last_scroll_value = self.chat.get_scroll_max_value()
            return

        print("[main GUI]: generated_reply")

        self.load_chatlog_info()
        self.chat_layout_update()
        # self.chat.scroll_to_animation()

    def get_chatlog_path(self):
        from setting_info import SettingInfo    # noqa
        return SettingInfo.get_chatlog_filename(self.char_info_dict["character_name"],True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
