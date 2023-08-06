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

from pathlib import Path

import time

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from PySide6.QtWidgets import *
from PySide6 import QtCore
from PySide6.QtCore import Qt

script_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.dirname(script_path)  # able to import modules in src folder

# IF MAIN THREAD IS THIS, APPEND SYS ENV PATH
if __name__ != "__main__":
    sys.path.append(script_path)
    sys.path.append(root_path)

from dracula_modules import *
from widgets import *

# Settings
from setting_info import SettingInfo, update_json, read_text_file  # noqa
# CHATLOAD
from dracula_modules.page_messages import Chat # Chat Widget
# AUDIO DEVICE
from modules.aud_device_manager import AudioDevice
import glob # find moegoe config file

#####################################################################################
#                                                                                   #
#                    Remove [import resources_rc] in ui_main.py!!                   #
#                                                                                   #
#####################################################################################

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

tts_wav_dir = os.path.join(os.path.dirname(root_path), 'cache', 'audio')
# tts_wav_path = Path(__file__).resolve().parent.parent / r'audio\tts.wav'

# Table column width size percentage values
t_val_col_a = 20   # Queue List column width_value
t_val_col_b = 60
t_val_col_c = 20

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # CHECK AUDIO CACHE FOLDER
        if not os.path.exists(tts_wav_dir):
            os.makedirs(tts_wav_dir)
            print("\033[34m" + f"[MainWindow.__init__]: Created audio cache folder! \033[33m[{tts_wav_dir}]" + "\033[0m")

        # SET CUSTOM VARIABLES
        self.char_info_dict : dict = None   # [your_name, character_name,
                                            # character_description, character_image,
                                            # greeting, context]

        self.chat_info_dict : dict = None   # <- Contains Chatlog + other_settings.txt
                                            # [chatlog, chatlog_filename,
                                            # discord_bot, discord_webhook,
                                            # discord_print_language, chat_display_language

        # TODO: create audio_setting, prompt setting (devcices)
        self.audio_info_dict: dict = None   # [mic_index, mic_threshold, phrase_timeout,

                                            # spk_index, tts_character_name, tts_language
                                            # voice_id, voice_speed, voice_volume,
                                            #  intonation_scale, pre_phoneme_length, post_phoneme_length]

        self.prompt_info_dict: dict = None  # [max_prompt_token, max_reply_token,
                                            # ai_model_language]

        # AUDIO DEVICE MANAGER
        self.newAudDevice = AudioDevice("compact")

        # SET AS GLOBAL WIDGETS
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        widgets.textBrowser.setOpenExternalLinks(True)
        widgets.textBrowser_google_colab_link.setOpenExternalLinks(True)
        self.chat = None
        self.last_scroll_value = -1

        # QTHREADS LIST
        self.tts_thread_list = []
        self.tts_thread_list.clear()
        self.prompt_thread_list = []
        self.prompt_thread_list.clear()

        self.thread_manager = THREADMANAGER(self)
        self.thread_manager.start()
        self.thread_manager.prompt_done_signal.connect(self.delete_first_prompt_thread)
        self.thread_manager.tts_gen_done_signal.connect(self.start_next_tts_thread)
        self.thread_manager.tts_speech_done_signal.connect(self.delete_first_tts_thread)
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

        global t_val_col_a, t_val_col_b, t_val_col_c
        # QTable for Thread Lists
        self.resize_thread_table(t_val_col_a, t_val_col_b, t_val_col_c)

        # Chat layout set Minsize
        widgets.chat.setMinimumSize(QSize(0, 300))

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
            self.extra_right_menu_update()

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # region UPDATE CONTENT BY COMPONENT
        widgets.checkBox_discord_bot.clicked.connect(self.update_content_by_component)
        widgets.checkBox_discord_webhook.clicked.connect(self.update_content_by_component)

        widgets.checkBox_tts_only.clicked.connect(self.update_content_by_component)

        widgets.pushButton_view_original_url.pressed.connect(self.update_content_by_component)
        widgets.pushButton_view_original_url.released.connect(self.released_component)

        # other settings components
        widgets.comboBox_discord_print_language.currentTextChanged.connect(self.update_content_by_component)
        widgets.lineEdit_discord_your_name.textChanged.connect(self.update_content_by_component)
        widgets.lineEdit_discord_your_avatar.textChanged.connect(self.update_content_by_component)
        # widgets.lineEdit_discord_bot_id.textChanged.connect(self.update_content_by_component)
        # widgets.lineEdit_discord_bot_channel_id.textChanged.connect(self.update_content_by_component)
        # widgets.lineEdit_discord_webhook_url.textChanged.connect(self.update_content_by_component)
        widgets.lineEdit_discord_webhook_username.textChanged.connect(self.update_content_by_component)
        widgets.lineEdit_discord_webhook_avatar.textChanged.connect(self.update_content_by_component)

        # character settings components
        widgets.textEdit_your_name.textChanged.connect(self.update_content_by_component)

        # prompt settings components

        # INSTALL EVENT FILTER
        widgets.lineEdit_api_url.installEventFilter(self)
        widgets.lineEdit_discord_bot_id.installEventFilter(self)
        widgets.lineEdit_discord_bot_channel_id.installEventFilter(self)
        widgets.lineEdit_discord_webhook_url.installEventFilter(self)

        widgets.lineEdit_api_url.installEventFilter(self)
        # endregion

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

        # print(self.convert_language_code("Japanese"))

    def resize_thread_table(self, per_a, per_b, per_c):
        global widgets
        for table in [widgets.tableWidget_prompt_list, widgets.tableWidget_tts_list]:
            table.setColumnWidth(0, table.width() * per_a / 100)
            table.setColumnWidth(1, table.width() * per_b / 100)
            table.setColumnWidth(2, table.width() * per_c / 100)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # DEFINE EVENT FILTER
    # ///////////////////////////////////////////////////////////////
    def eventFilter(self, source, event):
        global widgets
        if widgets is None:
            widgets = self.ui

        obj_name = source.objectName()
        component_type = None
        component_key = None
        component_property = None
        setting_name = None

        if obj_name is not None:
            component_type, component_key = self.component_info_by_name(obj_name)
        else:
            print("\033[31m" + f"Error [Main GUI.eventFilter]: can't get obj_name from source" + "\033[0m")
            return super().eventFilter(source, event)

        # print(f"source: {source}, event: {event}")

        if event.type() == QEvent.Type.FocusIn:
            if source == widgets.lineEdit_api_url:
                self.refresh_api_url(hide_url=False)
                if event.type() == QKeyEvent:
                    print(f"changing edit text: {source.text()} [{source.objectName()}]")

            if (source == widgets.lineEdit_discord_bot_id or
                source == widgets.lineEdit_discord_bot_channel_id or
                source == widgets.lineEdit_discord_webhook_url):
                self.refresh_discord_url(source, hide_url=False)
        elif event.type() == QEvent.Type.FocusOut:
            if source == widgets.lineEdit_api_url:
                setting_name = "prompt_settings"
            if (source == widgets.lineEdit_discord_bot_id or
                source == widgets.lineEdit_discord_bot_channel_id or
                source == widgets.lineEdit_discord_webhook_url):
                setting_name = "other_settings"

            # Get Text Data
            if isinstance(source, QLineEdit):
                comp_text = str(source.text())
                if not comp_text or comp_text == "":
                    comp_text = ""
                component_property = comp_text

            if isinstance(source, QTextEdit):
                comp_text = str(source.toPlainText())
                if not comp_text or comp_text == "":
                    comp_text = ""
                component_property = comp_text

            if component_key != None and component_property != None and setting_name != None:
                print("\033[34m" + f"[Main GUI.eventFilter]: Update \033[32m| {setting_name}.txt | {component_key} | {component_property}" + "\033[0m")
                update_json(component_key, component_property, setting_name)

            if source == widgets.lineEdit_api_url:
                self.refresh_api_url()
            if (source == widgets.lineEdit_discord_bot_id or
                source == widgets.lineEdit_discord_bot_channel_id or
                source == widgets.lineEdit_discord_webhook_url):
                self.refresh_discord_url(source)

        return super().eventFilter(source, event)


    # GUI COMPONENT CALLBACK
    # ///////////////////////////////////////////////////////////////
    def update_content_by_component(self):
        global widgets
        if widgets is None:
            widgets = self.ui

        called_component = self.sender()
        print(
            "\033[34m" + "called component: " +
            "\033[32m" + f"{called_component.objectName()}" +
            "\033[34m" + " | Type: " +
            "\033[32m" + f"{type(called_component).__name__}"
        )

        componentName = called_component.objectName()

        component_key = None
        component_type = None
        component_property = None
        setting_name = None


        if componentName is not None:
            component_type, component_key = self.component_info_by_name(componentName)

        # region CHARACTER SETTINGS
        #####################################################################################
        if componentName == "textEdit_your_name":
            setting_name = 'character_settings'
        #####################################################################################
        # endregion CHARACTER SETTINGS


        # region OTHER SETTINGS
        #####################################################################################
        if "discord_" in component_key or "tts_only" in component_key:
            setting_name = 'other_settings'
            if component_type == "checkBox":
                self.extra_right_menu_update(True)
        #####################################################################################
        # endregion OTHER SETTINGS


        # region PROMPT SETTINGS
        #####################################################################################
        if componentName == "pushButton_view_original_url":
            self.refresh_api_url(hide_url=False)     # peek api_url temporarily

            print("\033[34m" + f"{componentName}: \033[32mpressed\033[0m")
            return
        #####################################################################################
        # endregion PROMPT SETTINGS

        # PROPERTY HANDLER BY COMPONENT TYPE
        #####################################################################################
        if isinstance(called_component, QCheckBox):
            component_property = called_component.isChecked()

        if isinstance(called_component, QComboBox):
            if "language" in component_key:
                component_property = self.convert_language_code(called_component.currentText())
            else:
                component_property = called_component.currentText()

        if isinstance(called_component, QLineEdit):
            comp_text = str(called_component.text())
            if not comp_text or comp_text == "":
                comp_text = ""
            component_property = comp_text

        if isinstance(called_component, QTextEdit):
            comp_text = str(called_component.toPlainText())
            if not comp_text or comp_text == "":
                comp_text = ""
            component_property = comp_text
        #####################################################################################
        # endregion PROPERTY HANDLER


        # region Error Handler
        err_log = "\033[31m" + "Error [main GUI.update_content_by_component]:"
        # IF ANY INFORMATION IS NONE
        if componentName is None:
            print(f"{err_log} this component has no componentName: \033[33m{componentName}" + "\033[0m")
            return

        err_log = err_log + f" this \033[33m{componentName}\033[31m has no"
        if component_key is None:
            print(f"{err_log} component_key: \033[33m{component_key}" + "\033[0m")
            return
        if component_property is None and component_property != "":     # ignore string as Error
            print(f"{err_log} component_property: \033[33m{component_property}" + "\033[0m")
            return
        if setting_name is None:
            print(f"{err_log} setting_name: \033[33m{setting_name}" + "\033[0m")
            return
        # endregion

        print("\033[34m" + f"{component_key}: " + "\033[32m" + f"{component_property}" + "\033[0m")

        update_json(component_key, component_property, setting_name)

    def released_component(self):
        called_component = self.sender()
        componentName = called_component.objectName()

        # PROMPT SETTINGS
        #####################################################################################
        if componentName == "pushButton_view_original_url":
            self.refresh_api_url()  # Hide url

            print("\033[34m" + f"{componentName}: \033[32mreleased\033[0m")
            return
        #####################################################################################
        # PROMPT SETTINGS

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
            widgets.stackedWidget.setCurrentWidget(widgets.Prompt_Page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

            self.prompt_page_update()

        # SHOW AUDIO PAGE
        if btnName == "btn_audio_setting":
            widgets.stackedWidget.setCurrentWidget(widgets.Audio_Page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.load_audio_info()

        # SHARE BUTTON FROM EXTRA LEFT MENU
        if btnName == "btn_share":
            import webbrowser

            webbrowser.open('https://github.com/HWcomss/Blessing-AI')  # Go to Github Page
            print("Link BTN Clicked!")

        # EXIT PROGRAM
        if btnName == "btn_exit":
            print("Exit BTN Clicked!")
            QtCore.QCoreApplication.instance().quit()

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # [GUI] DRAW CHAT
    # ///////////////////////////////////////////////////////////////
    def chat_layout_update(self, dest_scroll_value = -1):
        global widgets
        ###########################################################################
        #   CHECK DIFFERENCE BETWEEN OLD / NOW CHATLOG
        ###########################################################################
        from LangAIComm import get_chatlog_info  # noqa
        if self.char_info_dict is None:
            print("[GUI] : Chat info dict is None, now loading character info...")
            self.load_character_info()
        new_chatlog_str = get_chatlog_info(self.char_info_dict["character_name"])

        if self.chat_info_dict:
            if self.chat_info_dict['chatlog'] == new_chatlog_str:
                print("\033[34m" + f"[main GUI.chat_layout_update]: Prev / Current Content of Chatlog are same! No need to update" + "\033[0m" )
                return

            elif self.last_scroll_value == dest_scroll_value and self.last_scroll_value != -1:
                print("\033[34m" + f"[main GUI.chat_layout_update]: scroll value is same! No need to scroll" + "\033[0m")
                return
        ###########################################################################
        #   END
        ###########################################################################
        self.load_chatlog_info()    # Load chatlog information

        if self.last_scroll_value == -1:
            self.last_scroll_value = 0
        elif self.chat:
                self.last_scroll_value = self.chat.get_scroll_value()
        else:
            print("\033[31m" + "Error [main GUI.chat_layout_update]: failed to load chat" + "\033[0m" )
            return 0

        # print(f"[main GUI.chat_layout_update]: last_scroll_value = {last_scroll_value}")


        ###########################################################################
        #   REFRESH CHAT
        ###########################################################################
        # REMOVE CHAT
        for chat in reversed(range(self.ui.chat_layout.count())):
            widgets.chat_layout.itemAt(chat).widget().deleteLater()
        self.chat = None

        # SET CHAT WIDGET
        self.chat = Chat(self, self.char_info_dict, self.chat_info_dict)

        # ADD WIDGET TO LAYOUT
        widgets.chat_layout.addWidget(self.chat)
        ###########################################################################
        #   END
        ###########################################################################


        # self.chat.set_scroll_value(last_scroll_value)
        self.chat.scroll_to_animation(last_value=self.last_scroll_value, value=dest_scroll_value)

    # [GUI] DRAW PROMPT PAGE
    # ///////////////////////////////////////////////////////////////
    def prompt_page_update(self):
        self.load_prompt_info()
        global widgets

        max_prompt_token = self.prompt_info_dict["max_prompt_token"]
        max_reply_token = self.prompt_info_dict["max_reply_token"]
        ai_model_language = self.convert_language_code(self.prompt_info_dict["ai_model_language"])

        self.refresh_api_url()

        widgets.lineEdit_max_prompt_token.setText( str(max_prompt_token) )
        widgets.horizontalSlider_max_prompt_token.setValue(max_prompt_token)

        widgets.lineEdit_max_reply_token.setText( str(max_reply_token) )
        widgets.horizontalSlider_max_reply_token.setValue(max_reply_token)

        widgets.comboBox_ai_model_language.setCurrentText(ai_model_language)

    def refresh_api_url(self, hide_url:bool=True):
        self.load_prompt_info()

        _widget = self.ui.lineEdit_api_url
        _url = self.prompt_info_dict["api_url"]

        self.refresh_url_widget(_widget, _url, hide_url, True)

    def refresh_discord_url(self, component:QLineEdit, hide_url=True):
        self.load_other_info()
        component_key = component.objectName().replace("lineEdit_", "")   # lineEdit_discord_bot_id
        # print(component_key)
        _url = self.chat_info_dict[component_key]

        self.refresh_url_widget(component, _url, hide_url, False)

    def refresh_url_widget(self, component:QObject, custom_url:str=None, hide_url:bool=True, add_prefix:bool=True):
        _final_url = custom_url

        if add_prefix:
            _final_url = self.prefix_url(_final_url)    # add 'http://' if there's no prefix

        if hide_url:
            _final_url = self.hide_url(_final_url, '●')  # convert _final_url to hidden_url

        if _final_url is None or _final_url == "":  # if url is blank
            print("\033[31m" + "Warning [main GUI.refresh_url_widget]: " + "\033[33m" + f"url is empty: { str(component.objectName()) }" + "\033[0m")

        component.setText(_final_url)    # LineEdit or TextEdit



    # [GUI] DRAW EXTRA RIGHT MENU
    # ///////////////////////////////////////////////////////////////
    def extra_right_menu_update(self, only_color = False):
        self.load_other_info()
        global widgets

        # INFO VARIABLES (PARENT CHECKBOX)
        ############################################################################################
        if not only_color:
            discord_bot = self.chat_info_dict["discord_bot"]
            discord_webhook = self.chat_info_dict["discord_webhook"]
            tts_only = self.chat_info_dict["tts_only"]

            # INFO VARIABLES
            ############################################################################################
            # Convert 'en' -> 'English'
            discord_print_language = self.convert_language_code( self.chat_info_dict["discord_print_language"] )

            # Unuse for now
            # chat_display_language = self.chat_info_dict["chat_display_language"]

            # DISCORD SHARED SETTING WIDGETS
            ############################################################################################
            widgets.comboBox_discord_print_language.setCurrentText(discord_print_language)

            # DISCORD BOT SETTING WIDGETS
            ############################################################################################
            widgets.checkBox_discord_bot.setChecked(discord_bot)
        else:
            discord_bot = widgets.checkBox_discord_bot.isChecked()
            discord_webhook = widgets.checkBox_discord_webhook.isChecked()
            tts_only = widgets.checkBox_tts_only.isChecked()

        bot_id_widget = widgets.lineEdit_discord_bot_id
        bot_channel_id_widget = widgets.lineEdit_discord_bot_channel_id

        if not only_color:
            # UPDATE TEXT WIDGETS
            ############################################################################################
            self.refresh_discord_url(bot_id_widget)             # Hide token
            self.refresh_discord_url(bot_channel_id_widget)     # Hide channel id

        self.color_by_state([bot_id_widget, bot_channel_id_widget]
                            , discord_bot)

        if not only_color:
            # DISCORD WEBHOOK SETTING WIDGETS
            ############################################################################################
            widgets.checkBox_discord_webhook.setChecked(discord_webhook)
            widgets.checkBox_tts_only.setChecked(tts_only)

        webhook_url_widget = widgets.lineEdit_discord_webhook_url
        webhook_username_widget = widgets.lineEdit_discord_webhook_username
        webhook_avatar_widget = widgets.lineEdit_discord_webhook_avatar
        discord_your_name_widget = widgets.lineEdit_discord_your_name
        discord_your_avatar_widget = widgets.lineEdit_discord_your_avatar

        if not only_color:
            # UPDATE TEXT WIDGETS
            ############################################################################################
            self.refresh_discord_url(webhook_url_widget)        # Hide token
            webhook_username_widget.setText(self.chat_info_dict["discord_webhook_username"])
            webhook_avatar_widget.setText(self.chat_info_dict["discord_webhook_avatar"])
            discord_your_name_widget.setText(self.chat_info_dict["discord_your_name"])
            discord_your_avatar_widget.setText(self.chat_info_dict["discord_your_avatar"])

        self.color_by_state([webhook_url_widget, webhook_username_widget, webhook_avatar_widget
                            , discord_your_name_widget, discord_your_avatar_widget], discord_webhook)



    def color_by_state(self, item_list: list, state = False):
        if not state:
            for item in item_list:
                item.setStyleSheet("")
            return

        for item in item_list:
            item.setStyleSheet("color: rgb(0, 255, 38);")

    def update_thread_table(self):
        global widgets
        table_list = [widgets.tableWidget_prompt_list, widgets.tableWidget_tts_list]
        threadlist_zip = [self.prompt_thread_list, self.tts_thread_list]
        row = 0

        for (table, thread_list) in zip(table_list, threadlist_zip):
            row_i = int(row/2)  # row [0, 1] -> index 0, [2, 3] -> index 1
            table.setRowCount(len(thread_list))
            if len(thread_list) >= 1:
                # print(row_i, table)
                table.setItem(row_i, 0, QTableWidgetItem("name"))
                table.setItem(row_i, 1, QTableWidgetItem(thread_list[row_i].text))

                if (thread_list[row_i].isRunning):
                    status = "running"
                else:
                    status = "Waiting"

                table.setItem(row_i, 2, QTableWidgetItem(status))

            row = row + 1



    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

        # Update Thread Table Columns Size
        global t_val_col_a, t_val_col_b, t_val_col_c
        self.resize_thread_table(t_val_col_a, t_val_col_b, t_val_col_c)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        # self.dragPos = event.globalPosition()
        self.dragPos = event.globalPos()  # deprecated

        # print(f"mouse position: {self.dragPos}")

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

        # UNFOCUS LINE EDIT IF CLICK OUTSIDE
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QLineEdit) or isinstance(focused_widget, QTextEdit):
            focused_widget.clearFocus()
            print("\033[34m" + f"Unfocus GUI Edit:\033[32m { focused_widget.objectName() }" + "\033[0m")
        # self.mousePressEvent(self, event)


    # LOAD INFO EVENTS
    # ///////////////////////////////////////////////////////////////
    def load_all_info(self):
        self.load_character_info()  # Load Character page

        self.chat_layout_update()    # Load Home Page

        self.load_audio_info()    # Load Audio page

        self.extra_right_menu_update()  # Load other information
        self.prompt_page_update() # Load prompt information


    def load_character_info(self):
        global widgets
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

        widgets.textEdit_your_name.setText(user_name)
        widgets.label_character_name.setText(character_name)

        # print(self.char_info_dict)


    def load_chatlog_info(self):
        global widgets

        if self.char_info_dict is None:
            print("[GUI] : Chat info dict is None, now loading character info...")
            self.load_character_info()

        if self.chat_info_dict is None:
            self.chat_info_dict = {}

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

    def refresh_audio_device(self):
        global widgets

        # REFRESH AUDIO DEVICE INFO LIST
        self.newAudDevice.get_all_device("compact")
        # print(self.newAudDevice.get_speaker_name_list())
        # print(self.newAudDevice)

        mic_comboBox = widgets.comboBox_mic_device
        spk_comboBox = widgets.comboBox_spk_device

        mic_comboBox.clear()
        spk_comboBox.clear()

        for _mic in self.newAudDevice.mic_list:
            mic_comboBox.addItem(_mic.name)
        for _spk in self.newAudDevice.speaker_list:
            spk_comboBox.addItem(_spk.name)

        # SET COLOR BY ITEM TEXT [None] OR NOT
        for _combo in [mic_comboBox, spk_comboBox]:
            self.add_none_item_combobox(_combo)

    def select_aud_devices_loaded_setting(self):
        self.newAudDevice.set_selected_device_to_default()  # TODO Load from audio_settings

        mic_comboBox = self.ui.comboBox_mic_device
        spk_comboBox = self.ui.comboBox_spk_device

        print("mic: ", self.newAudDevice.selected_mic)
        print("spk: ", self.newAudDevice.selected_speaker)
        mic_comboBox.setCurrentText(self.newAudDevice.selected_mic.name)
        spk_comboBox.setCurrentText(self.newAudDevice.selected_speaker.name)

        for _combo in [mic_comboBox, spk_comboBox]:
            if _combo.currentIndex() == 0:
                _col = "red"
            else:
                _col = "white"
            self.change_color_combobox(_combo, _col)

    # REFRESH TTS INFO LIST
    def refresh_tts_info(self):
        # region [TTS CHARACTER LIST]
        ################################################################################################
        tts_comboBox = widgets.comboBox_tts_charcter
        tts_comboBox.clear()

        tts_char_list = []
        tts_char_dir = os.path.join(root_path, 'Models', 'Voice')

        for _folder in os.scandir(tts_char_dir):
            if _folder.is_dir():
                tts_char_list.append(_folder.name)

        if len(tts_char_list) == 0:
            print(
                "\033[31m" + "Error [main GUI.refresh_tts_info]: Could not find any TTS Character folders in " + "\033[33m" + f"{tts_char_dir}" + "\033[0m")
            return None

        for tts_char in tts_char_list:
            tts_comboBox.addItem(tts_char)
        ################################################################################################
        # endregion [TTS CHARACTER LIST]

        # region [LOAD 'config.json' INFO]
        ################################################################################################
        cfg_path = os.path.join(tts_char_dir, self.audio_info_dict["tts_character_name"], "*.json")
        try:
            config_file = glob.glob(cfg_path)[0]
        except Exception as e:
            print(
                "\033[31m" + f"Error [main GUI.refresh_tts_info]: failed to search config file: \033[33m{e}" + "\n\033[0m")

        # print(f"moegoe config file: {config_file}")

        config_json = read_text_file(config_file)
        # print(f"settings [{config_json}]")

        # LANGUAGE LIST
        text_cleaners = config_json['data']['text_cleaners'][0]
        avbl_lang = self.get_available_language(text_cleaners)
        if not avbl_lang:
            print(
                "\033[31m" + "Error [main GUI.refresh_tts_info]: Could not find languge options from text cleaners " + "\033[33m" + f"{text_cleaners}" + "\033[0m")

        lang_comboBox = widgets.comboBox_tts_language
        lang_comboBox.clear()

        for _lang in avbl_lang:
            lang_comboBox.addItem(self.convert_language_code(_lang))

        # VOICE ID LIST
        id_list = config_json['speakers']
        voice_id_comboBox = widgets.comboBox_tts_voice_id
        voice_id_comboBox.clear()

        for _id in id_list:
            voice_id_comboBox.addItem(_id)
        ################################################################################################
        # endregion [LOAD 'config.json' INFO]

        for _combo in [tts_comboBox, lang_comboBox, voice_id_comboBox]:
            self.add_none_item_combobox(_combo)

        # region [UPDATE JSON FILE]
        ################################################################################################


        # update_json(tts_character_name, component_property, "audio_settings")
        ################################################################################################
        # endregion [UPDATE JSON FILE]

    # GET AVAILALBE LANG FROM 'text_cleaners'
    def get_available_language(self, text_cleaners):
        combo_list = []  # Warning! No support 'sanskrit' for now

        if "cjke_cleaners" in text_cleaners:
            combo_list.extend(['en', 'ja', 'ko', 'zh'])
        elif "zh_ja_mixture_cleaners" in text_cleaners:
            combo_list.extend(['ja', 'zh'])
        elif "japanese_cleaners" in text_cleaners:
            combo_list.extend(['ja'])
        elif "korean_cleaners" in text_cleaners:
            combo_list.extend(['ko'])
        elif "chinese_cleaners" in text_cleaners:
            combo_list.extend(['zh'])

        return combo_list

    def select_tts_loaded_setting(self, char_name, lang, v_id):
        tts_comboBox = self.ui.comboBox_tts_charcter
        lang_comboBox = self.ui.comboBox_tts_language
        voice_id_comboBox = self.ui.comboBox_tts_voice_id

        tts_comboBox.setCurrentText(char_name)
        lang_comboBox.setCurrentText(lang)

        # select [None] if there's no voice_id in list
        id_count = voice_id_comboBox.count()
        if id_count > 1 and v_id <= id_count-2:
            voice_id_comboBox.setCurrentIndex(v_id + 1)
        else:
            voice_id_comboBox.setCurrentIndex(0)

        # SET COLOR BY ITEM TEXT [None] OR NOT
        for _combo in [tts_comboBox, lang_comboBox, voice_id_comboBox]:
            # print(_combo.currentIndex())
            if _combo.currentIndex() == 0:
                _col = "red"
            else:
                _col = "white"
            self.change_color_combobox(_combo, _col)

    def change_color_combobox(self, combo_box:QComboBox, color:str):
        combo_style = "QComboBox {" \
                      "color: %s;" \
                      "background-color: rgb(27, 29, 35);" \
                      "border-radius: 5px;border: 2px;" \
                      " solid rgb(33, 37, 43);" \
                      "padding: 5px;padding-left: 10px;}"

        combo_box.setStyleSheet(combo_style % (color))


    def add_none_item_combobox(self, combo_box:QComboBox, text:str= "[None]", color:str= "red"):
        model = combo_box.model()
        combo_box.insertItem(0, text)
        model.setData(model.index(0, 0), QColor(color), QtCore.Qt.ForegroundRole)

    def load_audio_info(self):
        global widgets

        if self.audio_info_dict is None:
            self.audio_info_dict = {}

        self.audio_info_dict.update(SettingInfo.load_audio_settings())
        self.refresh_audio_device()
        self.refresh_tts_info()

        # region [LINEEDIT & SLIDERS]
        ################################################################################################
        mic_threshold = str (self.audio_info_dict["mic_threshold"])
        phrase_timeout = str (self.audio_info_dict["phrase_timeout"])
        voice_speed = str (self.audio_info_dict["voice_speed"])
        voice_volume = str ( int(self.audio_info_dict["voice_volume"] * 100))
        intonation_scale = str (self.audio_info_dict["intonation_scale"])
        pre_phoneme_length = str (self.audio_info_dict["pre_phoneme_length"])
        post_phoneme_length = str (self.audio_info_dict["post_phoneme_length"])

        widgets.lineEdit_mic_threshold.setText(mic_threshold + " %")
        widgets.horizontalSlider_mic_threshold.setValue(int(mic_threshold))

        widgets.lineEdit_phrase_timeout.setText(phrase_timeout)

        widgets.lineEdit_voice_volume.setText(voice_volume + " %")
        val = int(voice_volume)
        widgets.horizontalSlider_voice_volume.setValue(val)

        widgets.lineEdit_voice_speed.setText(voice_speed)
        val = int( float(voice_speed)*100.0)
        widgets.horizontalSlider_voice_speed.setValue(val)

        widgets.lineEdit_intonation_scale.setText(intonation_scale)
        val = int( float(intonation_scale)*100.0)
        widgets.horizontalSlider_intonation_scale.setValue(val)

        widgets.lineEdit_pre_phoneme_length.setText(pre_phoneme_length)
        val = int(float(pre_phoneme_length) * 100.0)
        widgets.horizontalSlider_pre_phoneme_length.setValue(val)

        widgets.lineEdit_post_phoneme_length.setText(post_phoneme_length)
        val = int(float(post_phoneme_length) * 100.0)
        widgets.horizontalSlider_post_phoneme_length.setValue(val)
        ################################################################################################
        # endregion [LINEEDIT & SLIDERS]

        # region [COMBO BOX]
        ################################################################################################
        mic_device = str(self.audio_info_dict["mic_index"])
        spk_device = str(self.audio_info_dict["spk_index"])
        tts_character_name = self.audio_info_dict["tts_character_name"]
        tts_language = self.convert_language_code(self.audio_info_dict["tts_language"])
        tts_voice_id = self.audio_info_dict["voice_id"]
        ################################################################################################
        # endregion [COMBO BOX]

        self.select_aud_devices_loaded_setting()
        self.select_tts_loaded_setting(tts_character_name, tts_language, tts_voice_id)

    def load_other_info(self):
        if self.chat_info_dict is None:
            self.chat_info_dict = {}

        self.chat_info_dict.update(SettingInfo.load_other_settings())

    def load_prompt_info(self):
        if self.prompt_info_dict is None:
            self.prompt_info_dict = {}

        self.prompt_info_dict.update(SettingInfo.load_prompt_settings())

    def after_generate_reply(self, success = 1):
        if success == -1:
            self.last_scroll_value = self.chat.get_scroll_value()
            self.chat.scroll_to_animation(last_value=self.last_scroll_value)
            self.last_scroll_value = self.chat.get_scroll_max_value()
            return

        print("\033[34m" + "[main GUI]: generated_reply" + "\033[0m")

        self.chat_layout_update()
        # self.chat.scroll_to_animation()

    def get_chatlog_path(self):
        return SettingInfo.get_chatlog_filename(self.char_info_dict["character_name"],True)

    def convert_language_code(self, language_input):
        """
        convert language code to full name of language or opposite.
        \n\n
        example)
            convert_language_code("en") -> "English"\n
            convert_language_code("English") -> "en"
        \n\n
        :param language_input: language code or full name of language
        :returns: An :py:class:`string` object.  
        """
        language_mapping = {
            # Add more language mappings as needed
            "English": "en",
            "Korean": "ko",
            "Japanese": "ja",
            "Chinese": "zh"
        }
        if language_input in language_mapping:
            return language_mapping[language_input]
        for key, value in language_mapping.items():
            if value == language_input:
                return key
        print(
            "\033[31m" + f"Error [main GUI.convert_language_code]: \033[33m{language_input}\033[31m is not supported: " + "\033[0m")
        return None

    def hide_url(self, url:str, mark:str='*'):
        """
        need 1 url as string list\n
        exmaple)
            url_test = "http://www.google.com"\n
            hide_url(url_test)
            \n\n
            returns 'http://**************'

        :param url: url to hide (:py:class:`str`)
        :param mark: hide with this character, defualt: '*'
        :returns: Hidden url (:py:class:`str`)
        """
        if url is None or url == "":    # if url is blank
            return None

        start_index = url.find("://")
        if start_index != -1:
            url_start = url.find("://") + 3
        else:
            url_start = 0
        hidden_url = url[:url_start] + mark * (len(url) - url_start)

        return hidden_url

    def prefix_url(self, url:str):
        """
                need 1 url as string list\n
                :param url: url to add http:// (:py:class:`str`)
                :returns: Prefixed url (:py:class:`str`)
        """
        if not url or url == "":    # if url is blank
            return None

        final_url = url
        if not url.startswith("http://") and not url.startswith("https://"):
            final_url = "http://" + url

        return final_url

    def component_info_by_name(self, componentName_str):
        parts = componentName_str.split('_')
        if len(parts) > 1:
            type_name = parts[0]
            component_name = '_'.join(parts[1:])
            return type_name, component_name
        else:
            return "\033[31m" + f"[main GUI.component_info_by_name]: Invalid input format: \033[33m{componentName_str}" + "\033[0m"

    def delete_first_prompt_thread(self):
        self.prompt_thread_list[0].remove_from_thread_list()

        self.after_generate_reply()

    def delete_first_tts_thread(self):
        self.tts_thread_list[0].remove_from_thread_list()

    def start_next_tts_thread(self):
        if len(self.tts_thread_list) > 1:    # threada has more than 2
            if self.tts_thread_list[1].isRunning(): return # return if thread is already running

            print("[Main GUI.start_next_tts_thread]: Starting next TTS thread")
            self.tts_thread_list[1].start()
        else:
            print("[Main GUI.start_next_tts_thread]: There's no next TTS thread in thread list! all TTS threads is done generating wav file ")

    # Generate and Play TTS Using QThread
    def gen_voice_thread(self, text):
        tts_thread = TTSTHREAD(self, text)
        self.tts_thread_list.append(tts_thread)
        # tts_thread.print_thread_list()
        # tts_thread.start()
        self.update_thread_table()

    # Generate Prompt Using QThread
    def gen_prompt_thread(self, text):
        prompt_thread = PROMPTTHREAD(self, text)
        self.prompt_thread_list.append(prompt_thread)
        # prompt_thread.print_thread_list()
        # prompt_thread.start()

        prompt_thread.PromptDone.connect(self.gen_voice_thread)
        self.update_thread_table()

class THREADMANAGER(QThread):
    prompt_done_signal = Signal()
    tts_gen_done_signal = Signal()
    tts_speech_done_signal = Signal()
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    def run(self):
        main_program = self.parent
        while True:
            prompt_thread_list = main_program.prompt_thread_list
            tts_thread_list = main_program.tts_thread_list

            if len(prompt_thread_list) >= 1:
                # Start first thread if not running
                if not prompt_thread_list[0].isRunning() and prompt_thread_list[0].reply_text == "":
                    prompt_thread_list[0].start()
                    print(f"start prompt thread: [{prompt_thread_list[0].text}]")

                # Check reply text
                first_index_reply = prompt_thread_list[0].reply_text
                prompt_thread_list[0].print_thread_list()
                # print(first_index_reply)

                if first_index_reply != "":
                    # print(self.parent.ui.textEdit_your_name.toPlainText())
                    # self.parent.gen_voice_thread(first_index_reply)

                    # thread_list[0].remove_from_thread_list()
                    self.prompt_done_signal.emit()

            if len(tts_thread_list) >= 1:
                # Start first thread if not running
                if not tts_thread_list[0].isRunning() and not tts_thread_list[0].gen.speech_done:
                    tts_thread_list[0].start()
                    print(f"start tts thread: [{tts_thread_list[0].text}]")

                tts_thread_list[0].print_thread_list()

                if tts_thread_list[0].gen.gen_done and not tts_thread_list[0].gen.speech_done:
                    print("tts wav file is generated: ", tts_thread_list[0].text, tts_thread_list[0].gen.gen_done)
                    # Start next thread
                    tts_thread_list[0].gen.play_voice()
                    self.tts_gen_done_signal.emit()

                if tts_thread_list[0].gen.speech_done:
                    print("tts process all done: ", tts_thread_list[0].text, tts_thread_list[0].gen.speech_done)
                    # Remove current thraed
                    self.tts_speech_done_signal.emit()

            time.sleep(0.3)


class PROMPTTHREAD(QThread):
    PromptDone = Signal(str)
    def __init__(self, parent, text="", logging=True):
        super().__init__(parent)
        self.parent = parent
        self.text = text
        self.logging = logging
        self.reply_text = ""

    def run(self):
        from generate import Generator
        gen = Generator()
        self.reply_text = gen.generate(self.text)

        print("reply created: ", self.reply_text)
        self.PromptDone.emit(self.reply_text)

        # time.sleep(1)
        # self.remove_from_thread_list()

    def remove_from_thread_list(self):
        self.parent.prompt_thread_list.remove(self)

    def print_thread_list(self):
        if self.logging:
            thread_logging_str = "==================== Prompt Thread List ===================="

            print("\033[32m" + thread_logging_str + "\033[0m")
            print(self.parent.prompt_thread_list)
            for i, qthread in enumerate(self.parent.prompt_thread_list):
                print(f"QThread ({i}): [{qthread.text}]")
            print("\033[32m" + thread_logging_str + "\033[0m")


class TTSTHREAD(QThread):
    TTSDone = Signal()
    def __init__(self, parent, text="", logging=True):
        from generate import GeneratorTTS

        super().__init__(parent)
        self.parent = parent
        self.gen = GeneratorTTS()

        self.text = text
        self.logging = True

    def run(self):
        global tts_wav_dir
        self.gen.audio_path = tts_wav_dir

        self.gen.speak_tts(text=self.text)

        # self.speak_tts(text=self.text)
        # self.remove_from_thread_list()

    def remove_from_thread_list(self):
        self.parent.tts_thread_list.remove(self)

    def print_thread_list(self):
        if self.logging:
            thread_logging_str = "==================== TTS Thread List ===================="

            print("\033[32m" + thread_logging_str + "\033[0m")
            print(self.parent.tts_thread_list)
            for i, qthread in enumerate(self.parent.tts_thread_list):
                print(f"QThread ({i}): [{qthread.text}] | Gen Done: {qthread.gen.gen_done} | Speech Done: {qthread.gen.speech_done}")
            print("\033[32m" + thread_logging_str + "\033[0m")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
