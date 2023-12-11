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

try:
    from dracula_modules import *
except Exception as e:
    if type(e).__name__ == 'ModuleNotFoundError':   # Auto Remove 'import resources_rc'
        file_path = os.path.join(script_path, 'dracula_modules', 'ui_main.py')
        # Read the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # Modify the lines to replace 'import resources_rc' with '# import resources_rc'
        for i, line in enumerate(lines):
            if 'import resources_rc' in line:
                lines[i] = '# ' + line
        # Write the modified lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)

        print(f"'import resources_rc' has been replaced with '# import resources_rc' in {file_path}")

from widgets import *

# Settings
from setting_info import SettingInfo, update_json, read_text_file, add_item_json, gender_settings_dir

# CHATLOAD
from dracula_modules.page_messages import Chat # Chat Widget
# AUDIO DEVICE
from modules.aud_device_manager import AudioDevice
import glob # find moegoe config file

# COLOR LOG
from modules.color_log import print_log

# GENERATOR FOR PROMPT, TTS
from generate import Generator, GeneratorSTT, GeneratorTTS
# BOT COMMAND
from modules.sing_command import BotCommand

# MIC RECORD & THRESHOLD
from modules.pygame_mic import MicRecorder

from modules.manage_folder import audio_cache_dir, char_json_dir, tts_char_dir, rvc_voice_dir, init_folders

#####################################################################################
#                                                                                   #
#                    Remove [import resources_rc] in ui_main.py!!                   #
#                                                                                   #
#####################################################################################

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

# tts_wav_path = Path(__file__).resolve().parent.parent / r'audio\tts.wav'

# Table column width size percentage values
t_val_col_a = 20   # Queue List column width_value
t_val_col_b = 60
t_val_col_c = 20

class MainWindow(QMainWindow):
    update_table_signal = Signal()
    update_threshold_gui_signal = Signal(float, QObject, bool)
    update_phrase_timeout_gui_signal = Signal(float, QObject)

    def __init__(self):
        QMainWindow.__init__(self)

        # CHECK NESSECARY FOLDERS
        init_folders()

        # SET CUSTOM VARIABLES
        self.char_info_dict : dict = None   # [your_name, character_name,
                                            # character_description, character_image,
                                            # greeting, context]

        self.chat_info_dict : dict = None   # <- Contains Chatlog + other_settings.txt
                                            # [chatlog, chatlog_filename,
                                            # discord_bot, discord_webhook,
                                            # discord_print_language, chat_display_language

        self.audio_info_dict: dict = None   # [mic_index, mic_threshold, sub_mic_index, sub_mic_threshold, main/sub_phrase_timeout,
                                            # max_stt_worker,

                                            # spk_index, speaker_volume,
                                            # tts_character, tts_language, voice_id,
                                            # voice_speed, intonation_scale, pre_phoneme_length, post_phoneme_length]

        self.prompt_info_dict: dict = None  # [max_prompt_token, max_reply_token,
                                            # ai_model_language]

        self.command_info_dict: dict = None # cmd_sing, use_rvc_model_tts_name, rvc_model,
                                            # rvc_index_rate, rvc_fast_search, rvc_auto_pitch (bool),
                                            # rvc_gender (radio), rvc_pitch, rvc_overwrite_final,
                                            # rvc_main_vocal, rvc_backup_vocal, rvc_music, rvc_master_gain


        # AUDIO DEVICE MANAGER
        self.newAudDevice = AudioDevice()
        # SET AS GLOBAL WIDGETS
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        widgets.textBrowser.setOpenExternalLinks(True)
        widgets.textBrowser_google_colab_link.setOpenExternalLinks(True)
        widgets.textBrowser_papago_token_link.setOpenExternalLinks(True)
        widgets.textBrowser_edit_character_link.setOpenExternalLinks(True)

        self.chat = None

        # STORE STYLESHEET
        self.default_stylesheet: dict = {}
        self.default_threshold_slider_stylesheet = self.ui.horizontalSlider_mic_threshold.styleSheet()
        self.default_timeout_slider_stylesheet = self.ui.horizontalSlider_main_phrase_timeout.styleSheet()

        self.disabled_gui_opacity = 0.5

        # QTHREADS LIST
        self.tts_thread_list = []
        self.tts_thread_list.clear()
        self.prompt_thread_list = []
        self.prompt_thread_list.clear()

        self.thread_manager = THREADMANAGER(self)
        self.thread_manager.start()
        # THREAD SIGNAL
        self.thread_manager.prompt_done_signal.connect(self.delete_first_prompt_thread)
        self.thread_manager.tts_gen_done_signal.connect(self.start_next_tts_thread)
        self.thread_manager.tts_play_done_signal.connect(self.delete_first_tts_thread)
        self.update_table_signal.connect(self.update_thread_table)      # updating table

        self.update_threshold_gui_signal.connect(self.update_threshold_gui)
        self.update_phrase_timeout_gui_signal.connect(self.update_phrase_timeout_gui)
        # TODO: [Fix Bug] when cmd_thread is playing audio,
        #   Also trying to add mode tts_thread, table update and threadmanager stops working..
        #   User name is not visible when generating RVC cover

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
        widgets.btn_command_setting.clicked.connect(self.buttonClick)
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

        # region [UPDATE CONTENT BY COMPONENT]
        ################################################################################################
        connect_comp_list = [
            ## other settings components
            widgets.checkBox_discord_bot,
            widgets.checkBox_discord_webhook,
            widgets.checkBox_tts_only,

            widgets.comboBox_discord_print_language,

            widgets.lineEdit_discord_your_name,
            widgets.lineEdit_discord_your_avatar,
            widgets.lineEdit_discord_webhook_username,
            widgets.lineEdit_discord_webhook_avatar,

            ## character settings components
            widgets.textEdit_your_name,
            widgets.textEdit_sub_user_name,
            widgets.comboBox_character_name,

            ## audio settings components
            widgets.pushButton_main_mic_toggle,
            widgets.pushButton_main_mic_toggle_home,
            widgets.pushButton_sub_mic_toggle,
            widgets.pushButton_sub_mic_toggle_home,
            widgets.pushButton_spk_toggle,

            widgets.comboBox_mic_device,
            widgets.comboBox_sub_mic_device,
            widgets.comboBox_spk_device,
            widgets.pushButton_mic_device_default,
            widgets.pushButton_sub_mic_device_default,
            widgets.pushButton_spk_device_default,

            widgets.lineEdit_mic_threshold,
            widgets.horizontalSlider_mic_threshold,
            widgets.pushButton_mic_threshold_default,
            widgets.lineEdit_sub_mic_threshold,
            widgets.horizontalSlider_sub_mic_threshold,
            widgets.pushButton_sub_mic_threshold_default,

            widgets.lineEdit_speaker_volume,
            widgets.horizontalSlider_speaker_volume,
            widgets.pushButton_speaker_volume_default,

            widgets.lineEdit_main_phrase_timeout,
            widgets.horizontalSlider_main_phrase_timeout,
            widgets.pushButton_main_phrase_timeout_default,
            widgets.lineEdit_sub_phrase_timeout,
            widgets.horizontalSlider_sub_phrase_timeout,
            widgets.pushButton_sub_phrase_timeout_default,

            widgets.comboBox_stt_language,
            widgets.pushButton_stt_language_default,
            widgets.spinBox_max_stt_worker,
            widgets.pushButton_max_stt_worker_default,

            widgets.comboBox_tts_character,
            widgets.comboBox_tts_language,
            widgets.comboBox_tts_voice_id,

            widgets.lineEdit_voice_speed,
            widgets.horizontalSlider_voice_speed,
            widgets.lineEdit_intonation_scale,
            widgets.horizontalSlider_intonation_scale,
            widgets.lineEdit_pre_phoneme_length,
            widgets.horizontalSlider_pre_phoneme_length,
            widgets.lineEdit_post_phoneme_length,
            widgets.horizontalSlider_post_phoneme_length,

            widgets.pushButton_voice_speed_default,
            widgets.pushButton_intonation_scale_default,
            widgets.pushButton_pre_phoneme_length_default,
            widgets.pushButton_post_phoneme_length_default,

            ## prompt settings components
            widgets.pushButton_view_original_url,
            widgets.pushButton_view_translator_id,
            widgets.pushButton_view_translator_secret,

            widgets.lineEdit_max_reply_token,
            widgets.horizontalSlider_max_reply_token,
            widgets.pushButton_max_reply_token_default,

            widgets.lineEdit_max_prompt_token,
            widgets.horizontalSlider_max_prompt_token,
            widgets.pushButton_max_prompt_token_default,

            widgets.comboBox_ai_model_language,

            ## command settings components
            widgets.horizontalGroupBox_cmd_sing,
            widgets.comboBox_rvc_model,
            widgets.checkBox_use_rvc_model_tts_name,

            widgets.lineEdit_rvc_index_rate,
            widgets.horizontalSlider_rvc_index_rate,
            widgets.pushButton_rvc_index_rate_default,

            widgets.radioButton_rvc_gender_male,
            widgets.radioButton_rvc_gender_female,

            widgets.checkBox_rvc_fast_search,
            widgets.horizontalGroupBox_rvc_auto_pitch,
            widgets.lineEdit_rvc_pitch,
            widgets.horizontalSlider_rvc_pitch,
            widgets.pushButton_rvc_pitch_default,

            widgets.checkBox_rvc_overwrite_final,

            widgets.lineEdit_rvc_main_vocal,
            widgets.horizontalSlider_rvc_main_vocal,
            widgets.pushButton_rvc_main_vocal_default,
            widgets.lineEdit_rvc_backup_vocal,
            widgets.horizontalSlider_rvc_backup_vocal,
            widgets.pushButton_rvc_backup_vocal_default,
            widgets.lineEdit_rvc_music,
            widgets.horizontalSlider_rvc_music,
            widgets.pushButton_rvc_music_default,
            widgets.lineEdit_rvc_master_gain,
            widgets.horizontalSlider_rvc_master_gain,
            widgets.pushButton_rvc_master_gain_default
        ]
        self.init_combobox_text(connect_comp_list)
        self.connect_components_with_update_method(connect_comp_list)

        ## INSTALL EVENT FILTER
        widgets.lineEdit_api_url.installEventFilter(self)
        widgets.lineEdit_translator_api_id.installEventFilter(self)
        widgets.lineEdit_translator_api_secret.installEventFilter(self)

        widgets.lineEdit_discord_bot_id.installEventFilter(self)
        widgets.lineEdit_discord_bot_channel_id.installEventFilter(self)
        widgets.lineEdit_discord_webhook_url.installEventFilter(self)

        self.install_event_all(QComboBox)
        self.install_event_all(QSlider)

        ################################################################################################
        # endregion [UPDATE CONTENT BY COMPONENT]

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

    def get_stylesheet_from_dict(self, comp: QObject, mod_function, args):
        '''
        search stylesheet from self.default_stylesheet (dict)

        if found -> return [stylesheet (str), modded_stylesheet (str)]
        else -> add info to dict and return [stylesheet, modded_stylesheet]
        '''
        key_str = comp.objectName()

        # Get Value from dict, if no key found value is None
        value = self.default_stylesheet.get(key_str)

        if value:
            # print(f'[{key_str}] key found in dict')
            result = value
        else:
            # print(f'[{key_str}] has not found, add to dict')
            style_sheet = comp.styleSheet()

            value = [style_sheet, mod_function(style_sheet, args)]
            self.default_stylesheet[key_str] = value

        # print(self.default_stylesheet)
        return value

    def change_stylesheet_opacity(self, stylesheet:str, factor:float):    # saturation 0.0~1.0
        import re
        def rgb_to_rgba(match):
            import colorsys
            r, g, b = map(int, match.groups())
            a = int(factor * 255.0)
            return f'rgba({r},{g},{b},{a})'

        pattern = re.compile(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')
        adjusted_str = pattern.sub(rgb_to_rgba, stylesheet)
        return adjusted_str

    def change_stylesheet_color(self, stylesheet:str, r:int, g:int, b:int, alpha:bool):
        if alpha:
            a = int(self.disabled_gui_opacity * 255.0)
        else:
            a = 255

        import re
        def rgb_to_rgba(match):
            import colorsys
            _r, _g, _b = map(int, match.groups())
            return f'rgba({r},{g},{b},{a})'

        pattern = re.compile(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')
        adjusted_str = pattern.sub(rgb_to_rgba, stylesheet)
        print(adjusted_str)
        return adjusted_str

    def resize_thread_table(self, per_a, per_b, per_c):
        global widgets
        for table in [widgets.tableWidget_prompt_list, widgets.tableWidget_tts_list]:
            table.setColumnWidth(0, table.width() * per_a / 100)
            table.setColumnWidth(1, table.width() * per_b / 100)
            table.setColumnWidth(2, table.width() * per_c / 100)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # CONNECT HANDLER BY TYPES
    def connect_components_with_update_method(self, obj_list:list[QObject]):
        for obj in obj_list:
            component_name = obj.objectName()
            if component_name is not None:
                component_type, component_key = self.component_info_by_name(component_name)

            if component_type == "lineEdit":
                obj.editingFinished.connect(self.update_content_by_component)
                # self.ui.lineEdit_discord_your_name.editingFinished.connect
                # self.ui.textEdit_your_name.textChanged
            elif component_type == "textEdit":
                obj.textChanged.connect(self.update_content_by_component)
            elif component_type in ["checkBox", "horizontalGroupBox", "radioButton"]:
                obj.toggled.connect(self.update_content_by_component)
                # widgets.checkBox_discord_webhook.clicked.connect(self.update_content_by_component)
            elif component_type == "comboBox":
                obj.activated.connect(self.update_content_by_component)
                # widgets.comboBox_discord_print_language.currentIndexChanged.connect(self.update_content_by_component)
            elif component_type == "pushButton":
                obj.pressed.connect(self.update_content_by_component)
                obj.released.connect(self.released_component)
                # widgets.pushButton_view_translator_secret
            elif component_type == "horizontalSlider":
                obj.valueChanged.connect(self.update_content_by_component)
            elif component_type == "spinBox":
                obj.valueChanged.connect(self.update_content_by_component)
            else:
                print(
                    "\033[31m" + f"Error [main GUI.connect_components_with_update_method]: not supported component: \033[33m{component_name}" + "\n\033[0m")
                raise ValueError("not supported component in obj_list")


    # region [DEFINE EVENT FILTER]
    #####################################################################################
    def eventFilter(self, source, event):
        global widgets
        if widgets is None:
            widgets = self.ui

        obj_name = source.objectName()

        # SCROLL EVENT HANDLER
        if event.type() == QEvent.Type.Wheel:
            if self.check_name(obj_name, ["comboBox", "horizontalSlider"]):
                scroll_widget = self.find_parent_qobject(source, "scrollArea_")
                if scroll_widget:
                    # print("scroll parent:", scroll_widget.objectName())
                    scroll_widget = scroll_widget.verticalScrollBar()
                else:
                    # print("no scrollArea found in page")
                    return True
                cur_scroll_val = scroll_widget.value()
                dir = -1 if event.angleDelta().y() > 0 else 1
                scroll_amount = 80 * dir

                # Simulate Scroll Event
                scroll_widget.setValue(cur_scroll_val + scroll_amount)

                # Ignore Original Event
                return True

        component_type = None
        component_key = None
        component_property = None
        setting_name = None

        if obj_name is not None:
            component_type, component_key = self.component_info_by_name(obj_name)
        else:
            print("\033[31m" + f"Error [Main GUI.eventFilter]: can't get obj_name from source" + "\033[0m")
            return super().eventFilter(source, event)

        # print(f"source: {source}, type: {event.type()}, event: {event}")

        lineEdit_api_url_list = [widgets.lineEdit_api_url]
        lineEdit_api_token_list = [widgets.lineEdit_translator_api_id, widgets.lineEdit_translator_api_secret]
        lineEdit_discord_list = [widgets.lineEdit_discord_bot_id, widgets.lineEdit_discord_bot_channel_id, widgets.lineEdit_discord_webhook_url]

        if event.type() == QEvent.Type.FocusIn:
            if source in lineEdit_api_url_list:
                self.refresh_api_url(hide_url=False)
                if event.type() == QKeyEvent:
                    print(f"changing edit text: {source.text()} [{obj_name}]")

            if source in lineEdit_api_token_list:
                self.refresh_api_token(source, hide_url=False)
                if event.type() == QKeyEvent:
                    print(f"changing edit text: {source.text()} [{obj_name}]")

            if source in lineEdit_discord_list:
                self.refresh_discord_url(source, hide_url=False)
        elif event.type() == QEvent.Type.FocusOut:
            if source in lineEdit_api_url_list or source in lineEdit_api_token_list:
                setting_name = "prompt_settings"
            if source in lineEdit_discord_list:
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

            if source in lineEdit_api_url_list:
                self.refresh_api_url()
            if source in lineEdit_api_token_list:
                self.refresh_api_token(source)
            if source in lineEdit_discord_list:
                self.refresh_discord_url(source)


        return super().eventFilter(source, event)

    def check_name(self, og_name, name_list:list):
        for name in name_list:
            if name in og_name:
                return True
        return False

    def install_event_all(self, obj_name:QObject):
        obj_list = self.findChildren(obj_name)

        for obj in obj_list:
            # install event on only custom objects
            if "_" in obj.objectName():
                obj.installEventFilter(self)

    #####################################################################################
    # endregion [DEFINE EVENT FILTER]


    # region [GUI COMPONENT CALLBACK]
    #####################################################################################
    def update_content_by_component(self):
        global widgets
        if widgets is None:
            widgets = self.ui

        called_component = self.sender()

        componentName = called_component.objectName()

        component_key = None
        component_type = None
        component_property = None
        setting_name = None

        if componentName is not None:
            component_type, component_key = self.component_info_by_name(componentName)


        # region [PROPERTY HANDLER BY COMPONENT TYPE]
        #####################################################################################
        component_key, component_property = self.get_property_by_qobj_type(called_component, component_key)
        #####################################################################################
        # endregion [PROPERTY HANDLER]


        # region CHARACTER SETTINGS
        #####################################################################################
        if componentName == "textEdit_your_name" or componentName == "textEdit_sub_user_name":
            setting_name = 'character_settings'

        if component_key in ["character_name"] and component_type == "comboBox":
            self.character_page_update(update_by_combo=True)

            return
        #####################################################################################
        # endregion CHARACTER SETTINGS


        # region AUDIO SETTINGS
        #####################################################################################
        ## mic/spk_device
        if component_type == "comboBox" and component_key in ["mic_device", "sub_mic_device", "spk_device"]:
            self.refresh_audio_device(update_by_combo=True)

            # Update mic_thread & adm
            self.thread_manager.mic_thread.check_mic_changed()
            self.thread_manager.sub_mic_thread.check_mic_changed()

            return
        if component_type == "pushButton" and "device_default" in component_key:
            _def_mic, _def_sub_mic, _def_spk = False, False, False
            if "sub_mic" in component_key:
                _def_sub_mic=True
            elif "mic" in component_key:
                _def_mic=True
            elif "spk" in component_key:
                _def_spk=True

            self.refresh_audio_device(True, _def_mic, _def_sub_mic, _def_spk)

            # Update mic_thread & adm
            self.thread_manager.mic_thread.check_mic_changed()
            self.thread_manager.sub_mic_thread.check_mic_changed()
            return

        percent_obj, decimal_obj = False, False

        ## region Synced or Only [lineEdit, Slider, PushButton] Handler | Also display value as [xx % / 0.xx]
        #####################################################################################
        if self.check_name(component_key, ["mic_threshold", "sub_mic_threshold", "speaker_volume"]):
            percent_obj = True
            setting_name = "audio_settings"
        elif self.check_name(component_key,
                             ["phrase_timeout", "voice_speed", "intonation_scale", "phoneme_length"]):
            decimal_obj = True
            setting_name = "audio_settings"

        elif self.check_name(component_key,
                           ["rvc_index_rate", "rvc_pitch", "rvc_main_vocal", "rvc_backup_vocal", "rvc_music", "rvc_master_gain"]):
            decimal_obj = True
            setting_name = "command_settings"


        if percent_obj or decimal_obj:
            if component_type == "lineEdit":
                if percent_obj:
                    conv_str = self.force_add_percent(called_component.text())  # 30 -> 30 %
                    conv_int = self.convert_percent_str(conv_str)   # 30 % -> 30
                    called_component.setText(conv_str)  # fix text (added ' %')
                    component_property = self.convert_percent_str(conv_str, decimal=True)  # 30 -> 0.3
                elif decimal_obj:
                    conv_dec = round(float(component_property), 2)   # 0.357 -> 0.36
                    conv_int = round(conv_dec, 2) * 100    # 0.36 -> 36
                    called_component.setText(str(conv_dec))  # Fix text (round float, 2nd)
                    component_property = conv_dec

                # Find QSlider & Sync Value
                synced_slider = self.find_qobject_by(component_key, QSlider, get_only_one=True)
                if synced_slider:
                    synced_slider.setValue(int(conv_int))
            elif component_type == "horizontalSlider":
                value_str = str(called_component.value())  # 70
                value_dec = int(value_str) * 0.01   # 70 -> 0.7
                value_dec = round(value_dec, 2) # 0.70001 -> 0.7

                if percent_obj:
                    conv_str = self.force_add_percent(value_str)    # 70 -> 70 %
                elif decimal_obj:
                    conv_str = str(value_dec)

                # Find QLineEdit & Sync Value
                synced_lineEdit = self.find_qobject_by(component_key, QLineEdit, get_only_one=True)
                if synced_lineEdit:
                    synced_lineEdit.setText(conv_str)
                component_property = value_dec    # 0.7
            elif component_type == "pushButton":
                reset_value = 0.0
                component_key = component_key.replace("_default", "")   # remove '_default' to find/update synced object

                if self.check_name(component_key, ["mic_threshold"]):
                    reset_value = 0.4
                elif self.check_name(component_key, ["phrase_timeout"]):
                    reset_value = 5.0
                elif self.check_name(component_key, ["intonation_scale"]):
                    reset_value = 1.5
                elif self.check_name(component_key, ["voice_speed", "speaker_volume", "phoneme_length"]):
                    reset_value = 1.0
                elif self.check_name(component_key, ["rvc_index_rate"]):
                    reset_value = 0.5
                else:
                    reset_value = 0.0   # (-10.0 ~ 10.0)

                component_property = reset_value

                # Find QSlider & Sync Value (lineEdit will automatically follow)
                synced_slider = self.find_qobject_by(component_key, QSlider, get_only_one=True)
                if synced_slider:
                    synced_slider.setValue(reset_value * 100)
                else:
                    print_log("error", "no slider found to reset", componentName)
        #####################################################################################
        ## endregion Synced or Only [lineEdit, Slider, PushButton] Handler

        ## ToggleButtons
        if component_key in ['main_mic_toggle', 'main_mic_toggle_home',
                             'sub_mic_toggle', 'sub_mic_toggle_home',
                             'spk_toggle']:
            return

        ## STT (Speach To Text Settings)
        # stt language
        elif 'stt_language' in component_key:
            setting_name = "audio_settings"
            if component_type == "pushButton":
                reset_value = 'any'
                component_key = component_key.replace("_default", "")
                component_property = reset_value

                synced_slider = self.find_qobject_by(component_key, QComboBox, get_only_one=True)
                if synced_slider:
                    synced_slider.setCurrentText(self.convert_language_code(reset_value))
                else:
                    print_log("error", "no slider found to reset", componentName)

        # stt max stt worker
        elif 'max_stt_worker' in component_key:
            setting_name = "audio_settings"
            if component_type == "pushButton":
                reset_value = 1
                component_key = component_key.replace("_default", "")
                component_property = reset_value

                synced_slider = self.find_qobject_by(component_key, QSpinBox, get_only_one=True)
                if synced_slider:
                    synced_slider.setValue(reset_value)
                else:
                    print_log("error", "no slider found to reset", componentName)

        # speaker volume
        elif component_key == "speaker_volume":
            if len (self.tts_thread_list) > 0:
                if self.tts_thread_list[0].gen:
                    self.tts_thread_list[0].gen.change_volume(component_property)

        ## Affect others by tts_character
        # [tts_character, tts_language, tts_voice_id]
        elif component_key in ["tts_character", "tts_language", "tts_voice_id"]:
            self.refresh_tts_info(update_by_combo=True)

            return
        #####################################################################################
        # endregion AUDIO SETTINGS


        # region PROMPT SETTINGS
        #####################################################################################
        if component_key in ["max_prompt_token", "max_reply_token",
                             "max_prompt_token_default", "max_reply_token_default"]:
            setting_name = "prompt_settings"
            if component_type == "lineEdit":
                value_str = float(called_component.text())
                conv_int = int(value_str)  # 80.3-> 80
                called_component.setText(str(conv_int))

                synced_slider = self.find_qobject_by(component_key, QSlider, get_only_one=True)
                if synced_slider:
                    synced_slider.setValue(conv_int)
                else:
                    print_log("error", "no slider found to reset", componentName)
                component_property = conv_int

            elif component_type == "horizontalSlider":
                value_int = int(called_component.value())  # 2048
                conv_str = str(value_int)

                # Find QLineEdit & Sync Value
                synced_lineEdit = self.find_qobject_by(component_key, QLineEdit, get_only_one=True)
                if synced_lineEdit:
                    synced_lineEdit.setText(conv_str)
                component_property = value_int

            elif component_type == "pushButton":
                reset_value = 0.0
                component_key = component_key.replace("_default", "")  # remove '_default' to find/update synced object

                if self.check_name(component_key, ["max_prompt_token"]):
                    reset_value = 2048
                elif self.check_name(component_key, ["max_reply_token"]):
                    reset_value = 100

                component_property = reset_value

                synced_slider = self.find_qobject_by(component_key, QSlider, get_only_one=True)
                if synced_slider:
                    synced_slider.setValue(reset_value)
                else:
                    print_log("error", "no slider found to reset", componentName)

        if "ai_model_language" in componentName:
            setting_name = "prompt_settings"

        if component_type == "pushButton" and "view" in component_key:
            if componentName == "pushButton_view_original_url":
                # URL format api
                self.refresh_api_url(hide_url=False)     # peek api_url temporarily
            else:
                # Token format api
                if componentName == "pushButton_view_translator_id":
                    _comp_api_lineEdit = self.ui.lineEdit_translator_api_id
                elif componentName == "pushButton_view_translator_secret":
                    _comp_api_lineEdit = self.ui.lineEdit_translator_api_secret

                self.refresh_api_token(_comp_api_lineEdit, hide_url=False)

            print("\033[34m" + f"{componentName}: \033[32mpressed\033[0m")
            return
        #####################################################################################
        # endregion PROMPT SETTINGS


        # endregion COMMAND SETTINGS
        #####################################################################################
        if component_key in ['rvc_index_rate', "use_rvc_model_tts_name", "rvc_fast_search", "rvc_overwrite_final"]:
            setting_name = 'command_settings'

        if "rvc_gender" in component_key:
            setting_name = 'command_settings'

            # update rvc_gender_settings.txt
            model_name = self.ui.comboBox_rvc_model.currentText()
            # model_name = self.command_info_dict['rvc_model']
            update_json(model_name, component_property, 'rvc_gender_settings', gender_settings_dir)

        if component_key in ["rvc_model"]:
            self.refresh_rvc_model(update_by_combo=True)

            return

        # Group Box
        if component_key in ['cmd_sing', 'rvc_auto_pitch']:
            setting_name = 'command_settings'

            # Mirror setEnable of 'rvc_auto_pitch' with 'rvc_manual_pitch'
            GB_rvc_auto_pitch = self.ui.horizontalGroupBox_rvc_auto_pitch
            GB_rvc_manaul_pitch = self.ui.verticalGroupBox_rvc_manual_pitch
            self.mirror_groupbox(GB_rvc_auto_pitch, GB_rvc_manaul_pitch)

        #####################################################################################
        # endregion COMMAND SETTINGS


        # region OTHER SETTINGS
        #####################################################################################
        if "discord_" in component_key or "tts_only" in component_key:
            setting_name = 'other_settings'
            if component_type == "checkBox":
                self.extra_right_menu_update(True)
        #####################################################################################
        # endregion OTHER SETTINGS


        # region Error Handler
        #####################################################################################
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
        #####################################################################################
        # endregion Error Handler

        print(
            "\033[34m" + "called component: " +
            "\033[32m" + f"{componentName}" +
            "\033[34m" + " | Type: " +
            "\033[32m" + f"{type(called_component).__name__}" +
            "\033[34m" + " | Property: " +
            "\033[32m" + f"{component_property}" +
            "\033[0m"
        )

        # print("\033[34m" + f"{component_key}: " + "\033[32m" + f"{component_property}" + "\033[0m")

        update_json(component_key, component_property, setting_name)

    # GUI Release Handler
    def released_component(self):
        called_component = self.sender()
        componentName = called_component.objectName()

        if componentName is not None:
            component_type, component_key = self.component_info_by_name(componentName)

        component_key, component_property = self.get_property_by_qobj_type(called_component, component_key)

        # region AUDIO SETTINGS
        #####################################################################################
        ## ToggleButtons
        if component_key in ['main_mic_toggle', 'main_mic_toggle_home',
                             'sub_mic_toggle', 'sub_mic_toggle_home',
                             'spk_toggle']:
            component_property = called_component.isChecked()

            # Change Button Text, Style by Bool
            if 'mic' in component_key:
                if 'main' in component_key:
                    pre_str = 'Main'
                    grp_box = self.ui.verticalGroupBox_main_mic
                else:
                    pre_str = 'Sub'
                    grp_box = self.ui.verticalGroupBox_sub_mic
                if 'home' in component_key:
                    checked_str, unchecked_str = f'{pre_str} Mic [ON]', f'{pre_str} Mic [OFF]'
                else:
                    checked_str, unchecked_str = 'Now Listening...', '[OFF]'

                self.set_groupbox_by_bool(grp_box, component_property, only_change_style=True)
            if 'spk' in component_key:
                checked_str, unchecked_str = 'Speaker ON', 'Speaker OFF'

                # Toggle tts_gen
                if len(self.tts_thread_list) > 0:
                    if self.tts_thread_list[0].gen:
                        self.tts_thread_list[0].gen.spk_toggle = component_property

                        cur_volume = str(self.ui.horizontalSlider_speaker_volume.value())
                        conv_str = self.force_add_percent(cur_volume)  # 30 -> 30 %
                        cur_volume = self.convert_percent_str(conv_str, decimal=True)  # 30 -> 0.3

                        self.tts_thread_list[0].gen.change_volume(cur_volume)


            component_key = component_key.replace("_home", "")

            self.set_toggle_button(called_component, component_property, checked_str, unchecked_str)
            setting_name = 'audio_settings'

        if '_default' in component_key:
            # No Property Save property from other
            return
        #####################################################################################
        # region AUDIO SETTINGS

        # region PROMPT SETTINGS
        #####################################################################################
        if component_type == "pushButton" and "view" in component_key:
            if componentName == "pushButton_view_original_url":
                # URL format api
                self.refresh_api_url()  # Hide url

            else:
                # Token format api
                if componentName == "pushButton_view_translator_id":
                    _comp_api_lineEdit = self.ui.lineEdit_translator_api_id
                elif componentName == "pushButton_view_translator_secret":
                    _comp_api_lineEdit = self.ui.lineEdit_translator_api_secret

                self.refresh_api_token(_comp_api_lineEdit)

            print("\033[34m" + f"{componentName}: \033[32mreleased\033[0m")
            return
        #####################################################################################
        # endregion PROMPT SETTINGS

        # region Error Handler
        #####################################################################################
        err_log = "\033[31m" + "Error [main GUI.released_component]:"

        # IF ANY INFORMATION IS NONE
        if componentName is None:
            print(f"{err_log} this component has no componentName: \033[33m{componentName}" + "\033[0m")
            return

        err_log = err_log + f" this \033[33m{componentName}\033[31m has no"
        if component_key is None:
            print(f"{err_log} component_key: \033[33m{component_key}" + "\033[0m")
            return
        if component_property is None and component_property != "":  # ignore string as Error
            print(f"{err_log} component_property: \033[33m{component_property}" + "\033[0m")
            return
        if setting_name is None:
            print(f"{err_log} setting_name: \033[33m{setting_name}" + "\033[0m")
            return
        #####################################################################################
        # endregion Error Handler

        print(
            "\033[34m" + "called component: " +
            "\033[32m" + f"{componentName}" +
            "\033[34m" + " | Type: " +
            "\033[32m" + f"{type(called_component).__name__}" +
            "\033[34m" + " | Property: " +
            "\033[32m" + f"{component_property}" +
            "\033[0m"
        )

        # print("\033[34m" + f"{component_key}: " + "\033[32m" + f"{component_property}" + "\033[0m")

        update_json(component_key, component_property, setting_name)

    # Property Handler (Get Property by QObject Types)
    def get_property_by_qobj_type(self, qobj:QObject, component_key:str):
        result_key = component_key
        result_property = None
        if isinstance(qobj, QCheckBox):
            result_property = qobj.isChecked()

        elif isinstance(qobj, QComboBox):
            if "language" in component_key:
                result_property = self.convert_language_code(qobj.currentText())
            else:
                result_property = qobj.currentText()

        elif isinstance(qobj, QLineEdit):
            comp_text = str(qobj.text())
            if not comp_text or comp_text == "":
                comp_text = ""
            result_property = comp_text

        elif isinstance(qobj, QTextEdit):
            comp_text = str(qobj.toPlainText())
            if not comp_text or comp_text == "":
                comp_text = ""
            result_property = comp_text

        elif isinstance(qobj, QGroupBox):
            result_property = qobj.isChecked()

        elif isinstance(qobj, QSpinBox):
            result_property = qobj.value()

        elif isinstance(qobj, QRadioButton):
            gender_radio, result_key = self.get_radio_object_by_name(component_key)
            result_property = self.get_radio_check(gender_radio).lower()  # female or male in radio button

        elif isinstance(qobj, QPushButton):
            if 'toggle' in component_key:
                result_property = qobj.isChecked()

        return result_key, result_property


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

            self.chat_layout_update()

        # SHOW CHARACTER PAGE
        if btnName == "btn_character":
            widgets.stackedWidget.setCurrentWidget(widgets.Character_page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.character_page_update()

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

            self.audio_page_update()

        if btnName == "btn_command_setting":
            widgets.stackedWidget.setCurrentWidget(widgets.Command_Page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.command_page_update()

        # SHARE BUTTON FROM EXTRA LEFT MENU
        if btnName == "btn_share":
            import webbrowser

            webbrowser.open('https://github.com/HWcoms/Blessing-AI')  # Go to Github Page
            print("Link BTN Clicked!")

        # EXIT PROGRAM
        if btnName == "btn_exit":
            print("Exit BTN Clicked!")
            QtCore.QCoreApplication.instance().quit()

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')
    #####################################################################################
    # endregion [GUI COMPONENT CALLBACK]

    # [GUI] GUI DRAW PAGE
    # ///////////////////////////////////////////////////////////////

    # region [DRAW CHAT PAGE]
    #####################################################################################
    def chat_layout_update(self, dest_scroll_value=-1):
        global widgets
        last_scroll_value = -1

        from LangAIComm import get_chatlog_info  # noqa
        if self.char_info_dict is None:
            print("[GUI.chat_layout_update] : Chat info dict is None, now loading character info...")
            self.character_page_update()
        else:
            self.load_character_info()  # Refresh Character Info [need character_name]

        # If Character JSON is not exist
        if self.char_info_dict["rescode"] == False:
            # REMOVE CHAT
            for chat in reversed(range(self.ui.chat_layout.count())):
                widgets.chat_layout.itemAt(chat).widget().deleteLater()
            self.chat = None
            refresh_chat = False
            self.chat_info_dict = None  # refresh chat next time
        else:
            new_chatlog_str = get_chatlog_info(self.char_info_dict["character_name"])

            refresh_chat = False

            ###########################################################################
            #   CHECK DIFFERENCE BETWEEN OLD / NOW CHATLOG
            ###########################################################################
            if not self.chat_info_dict:
                refresh_chat = True
            else:
                # check chat_info_dict has "chatlog" key
                if "chatlog" in self.chat_info_dict:
                    if self.chat_info_dict["chatlog"] == new_chatlog_str:
                        print("\033[34m" + f"[main GUI.chat_layout_update]: Prev / Current Content of Chatlog are same! No need to update" + "\033[0m" )
                    else:
                        refresh_chat = True
                else:
                    refresh_chat = True

            if refresh_chat:
                print("\033[34m" + f"[main GUI.chat_layout_update]: Loading ChatLog info!" + "\033[0m")
                self.load_chatlog_info()  # Load chatlog information
            ###########################################################################
            #   END
            ###########################################################################

        if self.chat:
            last_scroll_value = self.chat.get_scroll_value()

            if last_scroll_value != self.chat.get_scroll_max_value():
                dest_scroll_value = -2  # scroll to end

            self.chat.last_scroll_value = last_scroll_value
            self.chat.dest_scroll_value = dest_scroll_value

        # print("last: ", last_scroll_value, "dest: ", dest_scroll_value)

        ###########################################################################
        #   REFRESH CHAT
        ###########################################################################
        if refresh_chat:
            # REMOVE CHAT
            for chat in reversed(range(self.ui.chat_layout.count())):
                widgets.chat_layout.itemAt(chat).widget().deleteLater()
            self.chat = None

            # SET CHAT WIDGET
            self.chat = Chat(self, self.char_info_dict, self.chat_info_dict, last_scroll_value, dest_scroll_value)

            # ADD WIDGET TO LAYOUT
            widgets.chat_layout.addWidget(self.chat)

            # TODO: change token count labels to other (unnecessary items + using for other debug for now)
            ###########################################################################
            #   END
            ###########################################################################

        # region [Refresh Home PushButtons]
        ####################################################################
        self.load_audio_info()
        main_mic_toggle_value = self.audio_info_dict["main_mic_toggle"]
        sub_mic_toggle_value = self.audio_info_dict["sub_mic_toggle"]
        spk_toggle_value = self.audio_info_dict["spk_toggle"]

        checked_str, unchecked_str = 'Mic [ON]', 'Mic [OFF]'
        pre_str = 'Main'
        self.set_toggle_button(widgets.pushButton_main_mic_toggle_home, main_mic_toggle_value,
                               f'{pre_str} {checked_str}', f'{pre_str} {unchecked_str}')
        pre_str = 'Sub'
        self.set_toggle_button(widgets.pushButton_sub_mic_toggle_home, sub_mic_toggle_value,
                               f'{pre_str} {checked_str}', f'{pre_str} {unchecked_str}')

        self.set_toggle_button(widgets.pushButton_spk_toggle, spk_toggle_value, 'Speaker ON', 'Speaker OFF')
        ####################################################################
        # endregion [Refresh Home PushButtons]

        # update_thread_table
        self.update_thread_table()

    #####################################################################################
    # endregion [DRAW CHAT PAGE]

    # region [DRAW CHARACTER PAGE]
    #####################################################################################
    def character_page_update(self, update_by_combo=False):
        self.refresh_character_json(update_by_combo)

        global widgets
        character_name = self.char_info_dict["character_name"]
        user_name = self.char_info_dict["your_name"]
        sub_user_name = self.char_info_dict["sub_user_name"]

        if self.char_info_dict["rescode"] == False: # Failed to get JSON Info
            print_log("error", "char_dict load failed")
            widgets.textEdit_greeting.setText("")
            widgets.textEdit_context.setText("")
            widgets.textEdit_your_name.setText(user_name)
            widgets.textEdit_sub_user_name.setText(sub_user_name)
            return None

        bot_image = self.char_info_dict["character_image"]

        if bot_image is not None:
            # bot_pixmap = QPixmap.fromImage(bot_image)
            widgets.label_char_img.setPixmap(QPixmap(bot_image))
        else:
            widgets.label_char_img.clear()

        widgets.textEdit_greeting.setText(self.char_info_dict["greeting"])
        widgets.textEdit_context.setText(self.char_info_dict["context"])

        widgets.textEdit_your_name.setText(user_name)
        widgets.textEdit_sub_user_name.setText(sub_user_name)

        # print(self.char_info_dict)
    #####################################################################################
    # endregion [DRAW CHARACTER PAGE]

    # region [DRAW AUDIO PAGE]
    #####################################################################################
    def audio_page_update(self):
        self.load_audio_info()

        self.refresh_audio_device()
        self.refresh_tts_info()

        # region [PushButton]
        ################################################################################################
        # Toggle Spk & Main Mic / Sub Mic
        main_mic_toggle_value = self.audio_info_dict["main_mic_toggle"]
        sub_mic_toggle_value = self.audio_info_dict["sub_mic_toggle"]
        spk_toggle_value = self.audio_info_dict["spk_toggle"]

        checked_str, unchecked_str = 'Now Listening...', '[OFF]'
        self.set_toggle_button(widgets.pushButton_main_mic_toggle, main_mic_toggle_value, checked_str, unchecked_str)
        self.set_toggle_button(widgets.pushButton_sub_mic_toggle, sub_mic_toggle_value, checked_str, unchecked_str)

        # Grey Out GROUPS When Toggle is OFF
        main_mic_group = widgets.verticalGroupBox_main_mic
        sub_mic_group = widgets.verticalGroupBox_sub_mic
        self.set_groupbox_by_bool(main_mic_group, main_mic_toggle_value, only_change_style=True)
        self.set_groupbox_by_bool(sub_mic_group, sub_mic_toggle_value, only_change_style=True)

        ################################################################################################
        # endregion [PushButton]

        # region [LINEEDIT & SLIDERS]
        ################################################################################################
        main_phrase_timeout = str(self.audio_info_dict["main_phrase_timeout"])
        sub_phrase_timeout = str(self.audio_info_dict["sub_phrase_timeout"])
        widgets.lineEdit_main_phrase_timeout.setText(main_phrase_timeout)
        widgets.lineEdit_sub_phrase_timeout.setText(sub_phrase_timeout)

        self.set_qobjects_by_dict([widgets.lineEdit_mic_threshold, widgets.horizontalSlider_mic_threshold,
                                   widgets.lineEdit_sub_mic_threshold, widgets.horizontalSlider_sub_mic_threshold,
                                   widgets.lineEdit_speaker_volume, widgets.horizontalSlider_speaker_volume],
                                  self.audio_info_dict, 100, True)

        self.set_qobjects_by_dict([widgets.lineEdit_main_phrase_timeout, widgets.horizontalSlider_main_phrase_timeout,
                                   widgets.lineEdit_sub_phrase_timeout, widgets.horizontalSlider_sub_phrase_timeout,
                                   widgets.lineEdit_voice_speed, widgets.horizontalSlider_voice_speed,
                                   widgets.lineEdit_intonation_scale, widgets.horizontalSlider_intonation_scale,
                                   widgets.lineEdit_pre_phoneme_length, widgets.horizontalSlider_pre_phoneme_length,
                                   widgets.lineEdit_post_phoneme_length, widgets.horizontalSlider_post_phoneme_length],
                                  self.audio_info_dict, 100)

        ################################################################################################
        # endregion [LINEEDIT & SLIDERS]

        # ComboBox
        widgets.comboBox_stt_language.clear()
        for _lang in ['any', 'en', 'ja', 'ko', 'zh']:
            widgets.comboBox_stt_language.addItem(self.convert_language_code(_lang))

        widgets.comboBox_stt_language.setCurrentText(
            self.convert_language_code(
                self.audio_info_dict["stt_language"]
            )
        )

        # SpinBox
        widgets.spinBox_max_stt_worker.setValue(self.audio_info_dict["max_stt_worker"])

    def refresh_audio_device(self, update_by_combo = False, def_mic=False, def_sub_mic=False, def_spk=False):
        global widgets

        # REFRESH AUDIO DEVICE INFO LIST
        self.newAudDevice.get_all_device()

        mic_comboBox = widgets.comboBox_mic_device
        sub_mic_comboBox = widgets.comboBox_sub_mic_device
        spk_comboBox = widgets.comboBox_spk_device

        pre_mic_ = mic_comboBox.currentIndex()
        pre_sub_mic_ = sub_mic_comboBox.currentIndex()
        pre_spk_ = spk_comboBox.currentIndex()

        mic_comboBox.clear()
        sub_mic_comboBox.clear()
        spk_comboBox.clear()

        for _mic in self.newAudDevice.mic_list:
            mic_comboBox.addItem(_mic.name)
            sub_mic_comboBox.addItem(_mic.name)
        for _spk in self.newAudDevice.speaker_list:
            spk_comboBox.addItem(_spk.name)

        # SET COLOR BY ITEM TEXT [None] OR NOT
        for _combo in [mic_comboBox, sub_mic_comboBox, spk_comboBox]:
            self.add_none_item_combobox(_combo)

        _mic_index = None
        _sub_mic_index = None
        _spk_index = None

        if update_by_combo:
            _mic_index = pre_mic_ - 1
            _sub_mic_index = pre_sub_mic_ - 1
            _spk_index = pre_spk_ - 1
        else:
            _mic_index = self.audio_info_dict['mic_index']
            _sub_mic_index = self.audio_info_dict['sub_mic_index']
            _spk_index = self.audio_info_dict['spk_index']

        _mic_i_fix, _sub_mic_i_fix, _spk_i_fix = self.select_aud_devices_loaded_setting(_mic_index, _sub_mic_index, _spk_index, def_mic, def_sub_mic, def_spk)

        # region [UPDATE JSON FILE]
        ################################################################################################
        update_json("mic_index", _mic_i_fix, "audio_settings")
        update_json("sub_mic_index", _sub_mic_i_fix, "audio_settings")
        update_json("spk_index", _spk_i_fix, "audio_settings")
        ################################################################################################
        # endregion [UPDATE JSON FILE]

    def select_aud_devices_loaded_setting(self, _mic_i, _sub_mic_i, _spk_i, def_mic, def_sub_mic, def_spk):
        mic_comboBox = self.ui.comboBox_mic_device
        sub_mic_comboBox = self.ui.comboBox_sub_mic_device
        spk_comboBox = self.ui.comboBox_spk_device

        _ret_mic_i = _mic_i
        _ret_sub_mic_i = _sub_mic_i
        _ret_spk_i = _spk_i

        # Set devices with index
        if _mic_i < 0:
            mic_comboBox.setCurrentIndex(0)
            self.newAudDevice.selected_mic = None
        else:
            self.newAudDevice.set_selected_mic_index(_mic_i)
            _ret_mic_i = self.newAudDevice.selected_mic.index

        if _sub_mic_i < 0:
            sub_mic_comboBox.setCurrentIndex(0)
            self.newAudDevice.selected_sub_mic = None
        else:
            self.newAudDevice.set_selected_sub_mic_index(_sub_mic_i)
            _ret_sub_mic_i = self.newAudDevice.selected_sub_mic.index

        if _spk_i < 0:
            spk_comboBox.setCurrentIndex(0)
            self.newAudDevice.selected_speaker = None
        else:
            self.newAudDevice.set_selected_speaker_index(_spk_i)
            _ret_spk_i = self.newAudDevice.selected_speaker.index

        # Set Default devices if need
        self.newAudDevice.set_selected_device_to_default(def_mic, def_sub_mic, def_spk)

        if self.newAudDevice.selected_mic:
            _ret_mic_i = self.newAudDevice.selected_mic.index
        if self.newAudDevice.selected_sub_mic:
            _ret_sub_mic_i = self.newAudDevice.selected_sub_mic.index
        if self.newAudDevice.selected_speaker:
            _ret_spk_i = self.newAudDevice.selected_speaker.index

        if self.newAudDevice.selected_mic:
            mic_comboBox.setCurrentText(self.newAudDevice.selected_mic.name)
            print_log("log", "mic", self.newAudDevice.selected_mic)
        else:
            print_log("error", "mic", "None")
        if self.newAudDevice.selected_sub_mic:
            sub_mic_comboBox.setCurrentText(self.newAudDevice.selected_sub_mic.name)
            print_log("log", "sub_mic", self.newAudDevice.selected_sub_mic)
        else:
            print_log("error", "sub_mic", "None")
        if self.newAudDevice.selected_speaker:
            spk_comboBox.setCurrentText(self.newAudDevice.selected_speaker.name)
            print_log("log", "spk", self.newAudDevice.selected_speaker)
        else:
            print_log("error", "spk", "None")


        for _combo in [mic_comboBox, sub_mic_comboBox, spk_comboBox]:
            if _combo.currentIndex() == 0:
                _col = "red"
            else:
                _col = "white"
            self.change_color_combobox(_combo, _col)

        return _ret_mic_i, _ret_sub_mic_i, _ret_spk_i

    # REFRESH TTS INFO LIST
    def refresh_tts_info(self, update_by_combo = False):
        pre_tts_char = self.ui.comboBox_tts_character.currentText()
        pre_tts_lang = self.ui.comboBox_tts_language.currentText()
        pre_tts_v_id = self.ui.comboBox_tts_voice_id.currentIndex()

        # region [TTS CHARACTER LIST]
        ################################################################################################
        tts_comboBox = self.ui.comboBox_tts_character
        tts_comboBox.clear()

        tts_char_list = []

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

        lang_comboBox = self.ui.comboBox_tts_language
        lang_comboBox.clear()

        voice_id_comboBox = self.ui.comboBox_tts_voice_id
        voice_id_comboBox.clear()

        for _combo in [tts_comboBox, lang_comboBox, voice_id_comboBox]:
            self.add_none_item_combobox(_combo)

        tts_comboBox.setCurrentText(pre_tts_char)   # set pre selected char
        # region [LOAD 'config.json' INFO]
        ################################################################################################
        if update_by_combo:     # refresh other infos by combo text changed
            self.audio_info_dict.update(SettingInfo.load_audio_settings())
            tts_character = self.ui.comboBox_tts_character.currentText()
        else:
            tts_character = self.audio_info_dict["tts_character"]
        cfg_path = None
        config_file = None
        avbl_lang = None

        if tts_character:
            cfg_path = os.path.join(tts_char_dir, tts_character, "*.json")

        try:
            config_file = glob.glob(cfg_path)[0]
        except Exception as e:
            print(
                "\033[31m" + f"Error [main GUI.refresh_tts_info]: failed to search config file: [{tts_character}] \033[33m{e}" + "\n\033[0m")

        # print(f"moegoe config file: {config_file}")

        if config_file is not None:
            config_json = read_text_file(config_file)
            # print(f"settings [{config_json}]")

            # LANGUAGE LIST
            text_cleaners = config_json['data']['text_cleaners'][0]
            avbl_lang = self.get_available_language(text_cleaners)
            if not avbl_lang:
                print(
                    "\033[31m" + "Error [main GUI.refresh_tts_info]: Could not find langauge options from text cleaners " + "\033[33m" + f"{text_cleaners}" + "\033[0m")

            for _lang in avbl_lang:
                lang_comboBox.addItem(self.convert_language_code(_lang))

            # VOICE ID LIST
            id_list = config_json['speakers']

            for _id in id_list:
                voice_id_comboBox.addItem(_id)
        else:
            self.ui.comboBox_tts_character.setCurrentIndex(0)
        ################################################################################################
        # endregion [LOAD 'config.json' INFO]

        self.select_tts_loaded_setting(tts_character, avbl_lang, pre_tts_lang, pre_tts_v_id)

        # region [UPDATE JSON FILE]
        ################################################################################################
        char_updated = self.ui.comboBox_tts_character.currentText()
        if char_updated == "[None]":
            char_updated = None
        lang_updated = self.convert_language_code(lang_comboBox.currentText())
        v_id_updated = self.ui.comboBox_tts_voice_id.currentIndex() - 1

        update_json("tts_character", char_updated, "audio_settings")
        update_json("tts_language", lang_updated, "audio_settings")
        update_json("tts_voice_id", v_id_updated, "audio_settings")
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

    def select_tts_loaded_setting(self, char_name, avbl_lang:list[str], pre_lang, pre_id):
        lang = self.audio_info_dict["tts_language"]
        v_id = self.audio_info_dict["tts_voice_id"]

        tts_comboBox = self.ui.comboBox_tts_character
        lang_comboBox = self.ui.comboBox_tts_language
        voice_id_comboBox = self.ui.comboBox_tts_voice_id

        tts_comboBox.setCurrentText(char_name)

        # select language
        if pre_lang and avbl_lang:
            if self.convert_language_code(pre_lang) in avbl_lang:
                lang_comboBox.setCurrentText(pre_lang)
            elif lang in avbl_lang:
                lang_comboBox.setCurrentText(self.convert_language_code(lang))
            elif len(avbl_lang) >= 1:   # select first language if there's at least 1 language
                lang_comboBox.setCurrentIndex(1)
        elif avbl_lang:
            if lang in avbl_lang:
                lang_comboBox.setCurrentText(self.convert_language_code(lang))
            elif len(avbl_lang) >= 1:  # select first language if there's at least 1 language
                lang_comboBox.setCurrentIndex(1)
        else:
            lang_comboBox.setCurrentIndex(0)

        # select voice_id
        id_count = voice_id_comboBox.count()
        if pre_id <= id_count-1 and pre_id >= 1:
            voice_id_comboBox.setCurrentIndex(pre_id)
        elif id_count > 1 and v_id <= id_count-2 and v_id >= 0 and not pre_id >= 0:
            voice_id_comboBox.setCurrentIndex(v_id + 1)
        elif id_count > 1:  # select first voice if there's at least 1 voice
            voice_id_comboBox.setCurrentIndex(1)
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

    #####################################################################################
    # endregion [DRAW AUDIO PAGE]

    # region [DRAW PROMPT PAGE]
    #####################################################################################
    def prompt_page_update(self):
        self.load_prompt_info()
        global widgets

        max_prompt_token = self.prompt_info_dict["max_prompt_token"]
        max_reply_token = self.prompt_info_dict["max_reply_token"]
        ai_model_language = self.convert_language_code(self.prompt_info_dict["ai_model_language"])

        self.refresh_api_url()

        lineEdit_api_token_list = [widgets.lineEdit_translator_api_id, widgets.lineEdit_translator_api_secret]

        for _token_comp in lineEdit_api_token_list:
            self.refresh_api_token(_token_comp)

        widgets.lineEdit_max_prompt_token.setText( str(max_prompt_token) )
        widgets.horizontalSlider_max_prompt_token.setValue(max_prompt_token)

        widgets.lineEdit_max_reply_token.setText( str(max_reply_token) )
        widgets.horizontalSlider_max_reply_token.setValue(max_reply_token)

        widgets.comboBox_ai_model_language.clear()
        for _lang in ['en', 'ja', 'ko']:
            widgets.comboBox_ai_model_language.addItem(self.convert_language_code(_lang))

        widgets.comboBox_ai_model_language.setCurrentText(ai_model_language)

    def refresh_api_url(self, hide_url:bool=True):
        self.load_prompt_info()

        _widget = self.ui.lineEdit_api_url
        _url = self.prompt_info_dict["api_url"]

        self.refresh_url_widget(_widget, _url, hide_url, True)

    def refresh_api_token(self, component:QLineEdit, hide_url:bool=True):
        self.load_prompt_info()
        component_key = component.objectName().replace("lineEdit_", "")  # lineEdit_translator_api_id

        _token = self.prompt_info_dict[component_key]
        self.refresh_url_widget(component, _token, hide_url, False)

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

    #####################################################################################
    # endregion [DRAW PROMPT PAGE]

    # region [DRAW COMMAND PAGE]
    #####################################################################################
    def command_page_update(self):
        self.load_command_info()
        global widgets

        self.refresh_rvc_model()

        # region [LINEEDIT & SLIDERS & CHECKBOX]
        self.set_qobjects_by_dict([
                                # GROUPBOX
                                widgets.horizontalGroupBox_cmd_sing, widgets.horizontalGroupBox_rvc_auto_pitch,
                                # LINEEIDT & SLIDERS
                                widgets.lineEdit_rvc_index_rate, widgets.horizontalSlider_rvc_index_rate,
                                widgets.lineEdit_rvc_pitch, widgets.horizontalSlider_rvc_pitch,
                                widgets.lineEdit_rvc_main_vocal,  widgets.horizontalSlider_rvc_main_vocal,
                                widgets.lineEdit_rvc_backup_vocal, widgets.horizontalSlider_rvc_backup_vocal,
                                widgets.lineEdit_rvc_music, widgets.horizontalSlider_rvc_music,
                                widgets.lineEdit_rvc_master_gain, widgets.horizontalSlider_rvc_master_gain,
                                # CHECK BOX
                                widgets.checkBox_use_rvc_model_tts_name, widgets.checkBox_rvc_fast_search,
                                widgets.checkBox_rvc_overwrite_final
                                ], self.command_info_dict, 100)

        # Mirror setEnable of 'rvc_auto_pitch' with 'rvc_manual_pitch'
        GB_rvc_auto_pitch = widgets.horizontalGroupBox_rvc_auto_pitch
        GB_rvc_manaul_pitch = widgets.verticalGroupBox_rvc_manual_pitch
        self.mirror_groupbox(GB_rvc_auto_pitch, GB_rvc_manaul_pitch)

        # endregion

    def set_groupbox_by_bool(self, grp_box:QGroupBox, bool_value:bool, only_change_style=False):
        if not only_change_style:
            grp_box.setEnabled(bool_value)
        else:
            # only change StyleSheets
            if bool_value:
                style_i = 0
            else:
                style_i = 1
            og_stylesheet = self.get_stylesheet_from_dict(grp_box, self.change_stylesheet_opacity,
                                                          self.disabled_gui_opacity)
            # Select Original or Disabled(opacity) StyleSheet by bool
            grp_box.setStyleSheet(og_stylesheet[style_i])

    def mirror_groupbox(self, checkbox_grp:QGroupBox, non_checkbox_grp:QGroupBox):
        checkbox_grp_enabled = checkbox_grp.isChecked() and checkbox_grp.isEnabled()
        # print(f"{checkbox_grp.isChecked()}, {non_checkbox_grp.isEnabled()}: ", checkbox_grp_enabled)
        non_checkbox_grp.setEnabled(not checkbox_grp_enabled)

        self.disable_rich_texts_color_in(checkbox_grp)
        self.disable_rich_texts_color_in(non_checkbox_grp)

    def disable_rich_texts_color_in(self, qobj:QObject):
        label_list = qobj.findChildren(QLabel)
        # print(label_list)
        _disabled_label_list = []

        if len(label_list) == 0:
            raise RuntimeError(f"no label found in this QObject [{qobj}]")
        import re
        for _label in label_list:
            string_html = _label.text()

            # Define a regular expression pattern to remove <!-- and -->
            pattern = r'<!--color:(#[0-9a-fA-F]{6});-->'

            # Use re.sub to remove the comment markers
            uncommented_html = re.sub(pattern, lambda match: 'color:' + match.group(1) + ';', string_html)

            _label.setText(uncommented_html)
            if not _label.isEnabled():
                # Define a regular expression pattern to find color styles within span tags
                pattern = r'<span style="(.*?)color:(#[0-9a-fA-F]{6});">(.*?)<\/span>'

                # Use re.sub with a lambda function to replace the color styles
                result = re.sub(pattern, lambda match: '<span style="' + match.group(1) + '<!--color:' + match.group(
                    2) + ';-->' + '">' + match.group(3) + '</span>', string_html)
                _label.setText(result)

    def get_radio_object_by_name(self, key_name:str):
        _key_name = key_name.rsplit('_',1)[0]
        radios = self.find_qobject_by(_key_name, QRadioButton)   # list of radio btns
        if radios:
            return radios, _key_name

    def get_radio_check(self, radio_list: list[QRadioButton]):
        for radio in radio_list:
            if radio.isChecked():
                return radio.text()
        raise RuntimeError("No radio is checked Found")

    def set_radio_check(self, radio_list: list[QRadioButton], value):
        if value is None:
            raise ValueError("value is not specified!")

        for radio in radio_list:
            if value in radio.objectName():
                print_log("log", "RVC Gender", value, False)
                radio.setChecked(True)
                return radio

        raise RuntimeError("No radio is Found with value")

    #####################################################################################
    # endregion [DRAW COMMAND PAGE]

    # region [DRAW EXTRA RIGHT MENU]
    #####################################################################################
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
            widgets.comboBox_discord_print_language.clear()
            for _lang in ['en', 'ja', 'ko', 'zh']:
                widgets.comboBox_discord_print_language.addItem(self.convert_language_code(_lang))
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

    #####################################################################################
    # endregion [DRAW EXTRA RIGHT MENU]

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
        self.chat_layout_update()    # Load Home Page
        self.character_page_update()  # Load Character page
        self.audio_page_update()    # Load Audio page
        self.prompt_page_update() # Load prompt information
        self.command_page_update()  # Load Command Page

        self.extra_right_menu_update()  # Load other information

    # region [LOAD CHAT INFOS]
    ################################################################################################
    def load_chatlog_info(self):
        global widgets

        if self.char_info_dict is None:
            print("[GUI.load_chatlog_info] : Chat info dict is None, now loading character info...")
            self.character_page_update()
        else:
            # already calling load_character_info() in chat_layout_update()
            # self.load_character_info()  # Refresh Character Info [need character_name]
            pass

        if self.chat_info_dict is None:
            self.chat_info_dict = {}

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

        # widgets.textEdit_user_message.setText(last_user_message)
        # widgets.textEdit_bot_reply.setText(last_bot_reply)

        # get chatlog filename
        self.chat_info_dict["chatlog_filename"] = SettingInfo.get_chatlog_filename(character_name)

    def get_chatlog_path(self):
        return SettingInfo.get_chatlog_filename(self.char_info_dict["character_name"], True)

    ################################################################################################
    # endregion [LOAD CHAT INFOS]

    # region [LOAD CHARACTER INFOS]
    ################################################################################################
    def load_character_info(self):
        global widgets

        if self.char_info_dict is None:
            self.char_info_dict = {}

        self.char_info_dict.update(SettingInfo.load_character_settings())

        # override char_name / your_name in setting over json
        char_name_char_setting = self.char_info_dict["character_name"]
        your_name_char_setting = self.char_info_dict["your_name"]

        # region Load JSON / Profile Image
        from LangAIComm import get_character_info  # noqa
        char_dict = get_character_info(
            self.char_info_dict["character_name"])  # Dict [your_name, character_name, greeting, context, character_image]
        # print(char_dict)

        if not char_dict:
            print_log("error", "char_dict load failed")
            self.char_info_dict["rescode"] = False
            return False

        # bot_image = char_dict["character_image"]

        self.char_info_dict.update(char_dict)
        self.char_info_dict["character_name"] = char_name_char_setting  # override character_name as settings.txt
        self.char_info_dict["your_name"] = your_name_char_setting  # override your_name as settings.txt
        self.char_info_dict["rescode"] = True
        return True
        # endregion Load Profile Image

    def refresh_character_json(self, update_by_combo=False):
        character_comboBox = self.ui.comboBox_character_name

        if not update_by_combo:
            self.load_character_info()
            _character_name = self.char_info_dict["character_name"]

            # region [CHARACTER LIST]
            ################################################################################################
            character_comboBox.clear()

            char_json_list = []

            # check character folder name
            for _folder in os.scandir(char_json_dir):
                if _folder.is_dir():
                    char_json_list.append(_folder.name)

            if len(char_json_list) == 0:
                print_log("error", "Could not find any Character (JSON) folders in", f"{char_json_dir}")
                raise RuntimeError("No Character JSON file found! please Add Character Folder and put JSON File in it!")
                exit(0)

            for char_name in char_json_list:
                character_comboBox.addItem(char_name)

            if _character_name in char_json_list:
                print("test:" , f"found character {_character_name}")
                character_comboBox.setCurrentText(_character_name)
            else:
                print("test2:", f"Could not found character {_character_name}")
                character_comboBox.setCurrentIndex(0)

        char_name = character_comboBox.currentText()
        self.char_info_dict["character_name"] = char_name
        update_json("character_name", char_name, 'character_settings')

        self.load_character_info()  # refresh char info 1 more time

        return char_name
        ################################################################################################
        # endregion [CHARACTER LIST]

    ################################################################################################
    # endregion [LOAD CHARACTER INFOS]

    # region [LOAD AUDIO INFOS]
    ################################################################################################
    def load_audio_info(self):
        global widgets

        if self.audio_info_dict is None:
            self.audio_info_dict = {}

        self.audio_info_dict.update(SettingInfo.load_audio_settings())

    ################################################################################################
    # endregion [LOAD AUDIO INFOS]

    # region [LOAD COMMAND INFOS]
    ################################################################################################
    def load_command_info(self):
        global widgets

        if self.command_info_dict is None:
            self.command_info_dict = {}

        self.command_info_dict.update(SettingInfo.load_command_settings())

    def refresh_rvc_model(self, update_by_combo=False):
        rvc_model_comboBox = self.ui.comboBox_rvc_model

        if not update_by_combo:
            self.load_audio_info()
            _tts_model_name = self.audio_info_dict["tts_character"]
            _rvc_model_from_dict = self.command_info_dict['rvc_model']
            _use_tts_name = self.command_info_dict['use_rvc_model_tts_name']

            # region [RVC CHARACTER LIST]
            ################################################################################################
            rvc_model_comboBox.clear()

            rvc_char_list = []
            rvc_char_dir = rvc_voice_dir

            # check rvc_voice folder name, same as tts model
            for _folder in os.scandir(rvc_char_dir):
                if _folder.is_dir():
                    rvc_char_list.append(_folder.name)

            if len(rvc_char_list) == 0:
                print_log("error", "Could not find any RVC Character folders in", f"{tts_char_dir}")
                return None

            for rvc_char in rvc_char_list:
                rvc_model_comboBox.addItem(rvc_char)

            for _combo in [rvc_model_comboBox]:
                self.add_none_item_combobox(_combo)

            if _tts_model_name in rvc_char_list and _use_tts_name:
                rvc_model_comboBox.setCurrentText(_tts_model_name)
            elif _rvc_model_from_dict in rvc_char_list:
                rvc_model_comboBox.setCurrentText(_rvc_model_from_dict)
            else:
                rvc_model_comboBox.setCurrentIndex(0)

        rvc_model_name = rvc_model_comboBox.currentText()
        update_json("rvc_model", rvc_model_name, 'command_settings')

        self.check_gender_setting(rvc_model_name)

        gender_radio = [widgets.radioButton_rvc_gender_male, widgets.radioButton_rvc_gender_female]
        self.set_radio_check(gender_radio, self.command_info_dict['rvc_gender'])
        widgets.horizontalGroupBox_rvc_auto_pitch.setChecked(self.command_info_dict['rvc_auto_pitch'])

        return rvc_model_name
        ################################################################################################
        # endregion [RVC CHARACTER LIST]

    def check_gender_setting(self, rvc_model_name):
        # check cache folder exist
        settings_json = SettingInfo.load_rvc_gender_settings()

        key = rvc_model_name
        if rvc_model_name in settings_json:
            value = settings_json[key]
            update_json("rvc_gender", value, "command_settings")

        else:
            gender_radio = [self.ui.radioButton_rvc_gender_male, self.ui.radioButton_rvc_gender_female]
            value = self.get_radio_check(gender_radio).lower()  # female or male in radio button
            print_log("warning", f"model [{rvc_model_name}] doesn't have gender setting! Saving new", f"[{key}, {value}]")
            add_item_json(rvc_model_name, value, 'rvc_gender_settings', gender_settings_dir)
        self.command_info_dict["rvc_gender"] = value
    ################################################################################################
    # endregion [LOAD COMMAND INFOS]

    # region [LOAD MORE INFOS]
    ################################################################################################
    def load_other_info(self):
        if self.chat_info_dict is None:
            self.chat_info_dict = {}

        self.chat_info_dict.update(SettingInfo.load_other_settings())

    def load_prompt_info(self):
        if self.prompt_info_dict is None:
            self.prompt_info_dict = {}

        self.prompt_info_dict.update(SettingInfo.load_prompt_settings())

    ################################################################################################
    # endregion [LOAD MORE INFOS]

    # region [UTILS]
    #################################################################################################
    def set_toggle_button(self, button:QPushButton, bool_value:bool, on_text:str, off_text:str):
        if bool_value:
            button.setText(on_text)
        else:
            button.setText(off_text)
        button.setChecked(bool_value)

    def init_combobox_text(self, combo_list:list[QObject]):   # clear all QComboboxes in list
        for obj in combo_list:
            component_name = obj.objectName()
            if component_name is not None:
                component_type, component_key = self.component_info_by_name(component_name)

            if component_type == "comboBox":
                # print("cleared combobox: ", obj)
                obj.clear()

    def change_color_combobox(self, combo_box:QComboBox, color:str):
        if color == 'red':
            _c = '255,0,0'
        elif color == 'white':
            _c = '255,255,255'
        combo_style = "QComboBox {" \
                      f"color: rgb({_c});" \
                      "}"

        combo_box.setStyleSheet(combo_style)

    def add_none_item_combobox(self, combo_box:QComboBox, text:str= "[None]", color:str= "red"):
        model = combo_box.model()
        combo_box.insertItem(0, text)
        model.setData(model.index(0, 0), QColor(color), QtCore.Qt.ForegroundRole)

    def find_parent_qobject(self, child_object, search_name):
        _result = None
        _p = child_object.parent()
        while (_p.objectName() != "MainWindow" and _p != None):
            _p = _p.parent()
            if search_name in _p.objectName():
                _result = _p
                break
        # if _result:
        #     print("final: ", _result.objectName())
        return _result

    def find_qobject_by(self, name:str, type:QObject, get_only_one=False) -> QObject:
        """
        find 1 or List of :py:class:`QObject` by name and type

        Args:
            name: put name (:py:class:`str`)
            type: put type (:py:class:`QObject`)

        Returns:
            :py:class:`QObject` or List or None
        """

        # Error (not enough hints to find)
        if not type:
            print_log("error", "type should be specify to find QObject", f"name={name}, type={type}")
            raise ValueError()

        # Get matching QObjects list
        _found_obj_list = self.findChildren(type)

        if not name:
            return _found_obj_list

        _matching_obj_list = []
        for obj in _found_obj_list:
            if name in obj.objectName():
                _matching_obj_list.append(obj)

        if len(_matching_obj_list) == 1:
            return _matching_obj_list[0]
        elif len(_matching_obj_list) > 1:
            if get_only_one:
                # Try to get only exact same name
                for obj in _matching_obj_list:
                    _, cur_obj_name = self.component_info_by_name(obj.objectName())
                    if name == cur_obj_name:
                        return obj

            print_log("warning", "found multiple objs with", f"name={name},\n obj list={_matching_obj_list}")
            return _matching_obj_list

        print_log("warning", "Could not find any QObject with", f"name={name}, type={type}")
        return None

    def set_qobjects_by_dict(self, obj_list:list[QObject], _dict, value_multiplier=10.0, add_percent=False):
        """
        set value of QObjects in obj_list with certain pattern by _dict property
        Args:
            text: string to convert to a sequence
            cleaner_names: names of the cleaner functions to run the text through
        """
        for obj in obj_list:
            componentName = obj.objectName()
            if componentName is not None:
                component_type, component_key = self.component_info_by_name(componentName)

            res_value = _dict[component_key]

            res_str = ""
            if add_percent:
                res_int = int(res_value * value_multiplier)
                res_str = self.force_add_percent(str(res_int))
            else:
                res_str = str(res_value)

            if isinstance(obj, QLineEdit):
                obj.setText(res_str)
            elif isinstance(obj, QSlider):
                obj.setValue(int(res_value * value_multiplier))
            elif isinstance(obj, QCheckBox) or isinstance(obj, QGroupBox):
                obj.setChecked(res_value)
            else:
                raise ValueError("No QObject Found or Not Supported QObject")

    def force_add_percent(self, per_str:str):
        res_value = per_str
        if "%" not in res_value:
            res_value = res_value.strip()
            res_value += " %"
        elif " %" not in res_value:
            res_value = res_value.replace("%", " %")

        return res_value

    def convert_percent_str(self, per_str:str, decimal=False):
        res_value = per_str
        if "%" in res_value:
            res_value = res_value.replace("%", "")
            res_value.strip()

            res_value = int(float(res_value))
            if decimal:
                res_value = float(res_value) * 0.01
        else:
            if decimal:
                res_value = float(res_value) * 100.0
            res_value = int(res_value)
            res_value = str(res_value) + " %"

        return res_value
    #################################################################################################
    # endregion [UTILS]

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
            "Auto": "any",
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
        if language_input != '[None]':
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
            print ("\033[31m" + f"[main GUI.component_info_by_name]: Invalid input format: \033[33m{componentName_str}" + "\033[0m")
            return None, None

    # region [Thread Control Methods]
    #################################################################################################
    def after_generate_reply(self, success = 1):
        if success == -1:
            return

        print("\033[34m" + "[main GUI]: generated_reply" + "\033[0m")

        self.chat_layout_update()
        # self.chat.scroll_to_animation()

    def delete_first_prompt_thread(self):
        self.prompt_thread_list[0].remove_from_thread_list()
        self.update_thread_table()

        self.after_generate_reply()

    def delete_first_tts_thread(self):
        self.tts_thread_list[0].remove_from_thread_list()
        self.update_thread_table()

    def start_next_tts_thread(self):
        if len(self.tts_thread_list) > 1:    # threada has more than 2
            if self.tts_thread_list[1].isRunning(): return # return if thread is already running

            print("[Main GUI.start_next_tts_thread]: Starting next TTS thread")
            self.tts_thread_list[1].start()
        else:
            print("[Main GUI.start_next_tts_thread]: There's no next TTS thread in thread list! all TTS threads is done generating wav file ")

    def command_handler(self, cmd, value):
        if not cmd:
            self.gen_voice_thread(value)
        else:
            self.gen_command_thread(cmd, value)

    def gen_command_thread(self, cmd, text):
        cmd_thread = COMMANDTHREAD(self, cmd, text, logging=False)
        self.tts_thread_list.append(cmd_thread)

    # Generate and Play TTS Using QThread
    def gen_voice_thread(self, text):
        tts_thread = TTSTHREAD(self, text, logging=False)
        self.tts_thread_list.append(tts_thread)

    # Generate Prompt Using QThread
    def gen_prompt_thread_as_text(self, text):
        prompt_thread = PROMPTTHREAD(self, text=text, logging=False)
        self.prompt_thread_list.append(prompt_thread)

        prompt_thread.PromptDone.connect(self.command_handler)

    def gen_prompt_thread_as_audio(self, audio_file, audio_length):
        prompt_thread = PROMPTTHREAD(self, audio_file=audio_file, audio_length=audio_length, logging=False)
        self.prompt_thread_list.append(prompt_thread)

        prompt_thread.PromptDone.connect(self.command_handler)

    # Update QTable [Qthreads table]
    def update_thread_table(self):
        global widgets
        table_list = [widgets.tableWidget_prompt_list, widgets.tableWidget_tts_list]
        threadlist_zip = [self.prompt_thread_list, self.tts_thread_list]

        for (table, thread_list) in zip(table_list, threadlist_zip):
            table.setRowCount(len(thread_list))
            if len(thread_list) == 0:
                continue

            thread_index = 0
            for thread in thread_list:
                _class_type = type(thread).__name__
                _user = thread.character

                if _class_type == "TTSTHREAD":
                    _msg = '🔊 ' + thread.text
                    pass
                elif _class_type == "COMMANDTHREAD":
                    if thread.cmd_type == '!sing':
                        if thread.gen.auto_pitch_bool:
                            _user += f' [AutoP:{thread.gen.gender_type}]'
                        else:
                            _user += f' [Pitch:{thread.gen.pitch}]'
                        _type = '🎵'
                        if thread.gen.fast_search:
                            _type += '🚀'

                    _msg = f'{_type} ' + thread.text

                    pass
                else:   # PROMPTTHREAD
                    _msg = thread.text

                _is_running = '⏸️'
                if thread.isRunning():
                    _is_running = '▶️'

                table.setItem(thread_index, 0, QTableWidgetItem(thread.character))
                table.setItem(thread_index, 1, QTableWidgetItem(_msg))
                table.setItem(thread_index, 2, QTableWidgetItem(thread.state[1]))
                thread_index += 1

    # Update Mic Threshold GUI
    def update_threshold_gui(self, value, component:QObject, toggle:bool):  # toggle -> false: grey colored bar
        stop_x = value * 0.01

        if toggle:
            opacity = 255
        else:
            opacity = int(self.disabled_gui_opacity * 255.0)

        lines = self.default_threshold_slider_stylesheet.splitlines()
        lines[1] = f'\tbackground-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:{stop_x} rgba(11, 211, 0, {opacity}), stop:{stop_x+0.001} rgba(55, 62, 76, {opacity}));'
        # result_string = 'QSlider::groove {'+f'\tbackground-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:.5 rgb(11, 211, 0), stop:0.501 rgb(55, 62, 76));'+'}'
        result_string = '\n'.join(lines)

        component.setStyleSheet(result_string)

    # Update Phrase Timeout GUI
    def update_phrase_timeout_gui(self, remain_time, component:QObject):
        timeout_value = component.value() / 100.0
        stop_x =  remain_time / timeout_value

        # print(f'{round(remain_time,2)} / %: {round(stop_x,2)}')

        lines = self.default_timeout_slider_stylesheet.splitlines()
        lines[
            1] = f'\tbackground-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:{stop_x} rgb(11, 211, 0), stop:{stop_x + 0.001} rgb(55, 62, 76));'
        # result_string = 'QSlider::groove {'+f'\tbackground-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:.5 rgb(11, 211, 0), stop:0.501 rgb(55, 62, 76));'+'}'
        result_string = '\n'.join(lines)

        component.setStyleSheet(result_string)
    #################################################################################################
    # region [Thread Control Methods]


# region [Thread Classes & Static Methods]
#################################################################################################
class THREADMANAGER(QThread):
    prompt_done_signal = Signal()
    tts_gen_done_signal = Signal()
    tts_play_done_signal = Signal()

    max_stt_worker = 0  # [speech to text] max workers

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Mic
        self.mic_thread = MicRecorder(parent.ui.horizontalSlider_mic_threshold,
                                      parent.ui.horizontalSlider_main_phrase_timeout,
                                      is_sub=False)
        self.mic_thread.rec_duration = -1.0
        self.mic_thread.main_program = parent

        # Sub Mic
        self.sub_mic_thread = MicRecorder(parent.ui.horizontalSlider_sub_mic_threshold,
                                          parent.ui.horizontalSlider_sub_phrase_timeout,
                                          is_sub=True)
        self.sub_mic_thread.rec_duration = -1.0
        self.sub_mic_thread.main_program = parent
    def run(self):
        main_program = self.parent

        self.mic_thread.adm = main_program.newAudDevice
        self.sub_mic_thread.adm = main_program.newAudDevice

        while True:
            prompt_thread_list = main_program.prompt_thread_list
            tts_thread_list = main_program.tts_thread_list

            # PROMPT THREAD (STT + SEND PROMPT + CHECK CMD)
            if len(prompt_thread_list) >= 1: # if text or audio file entered
                self.max_stt_worker = self.parent.ui.spinBox_max_stt_worker.value()
                # print(self.max_stt_worker)
                avbl_stt_worker_count = max(self.max_stt_worker, len(prompt_thread_list))   # get max worker avbl

                # if first thread has text & ready -> Send Prompt Request
                if prompt_thread_list[0].text != '' and prompt_thread_list[0].state[0] == 'wait':
                    change_state(prompt_thread_list[0], "gen")
                    print(f"Start Send Prompt Request : [{prompt_thread_list[0].text}]")
                    pass

                stt_worker_count = 0
                waiting_thread_count = 0
                first_waiting_thread = None

                wait_threads_delete_after = []    # List of Waiting Threads should be delete after merging

                # Start all STT thread if not running
                # TODO: if waiting_thread > 1, merge all of threads text
                # Todo: prompt_thread needs username
                for i in range(len(prompt_thread_list)):
                    if stt_worker_count >= avbl_stt_worker_count:
                        print_log(f"STT_worker count over {stt_worker_count}/{avbl_stt_worker_count}")
                        break

                    # if Thread is not Running & in init state
                    if not prompt_thread_list[i].isRunning() and prompt_thread_list[i].state[0] == 'init':
                        prompt_thread_list[i].start()
                        # if audio input
                        if prompt_thread_list[i].text == '':
                            print(f"Start STT Thread[{i}]: [{prompt_thread_list[i].audio_length}] sec audio")

                    if prompt_thread_list[i].state[0] == 'wait':
                        if waiting_thread_count == 0:
                            first_waiting_thread = prompt_thread_list[i]
                        else:
                            wait_threads_delete_after.append(prompt_thread_list[i])

                        waiting_thread_count += 1

                    # if audio input
                    if prompt_thread_list[i].text == '':
                        stt_worker_count += 1

                # Merge and Delete Waiting Threads
                for wait_thread in wait_threads_delete_after:
                    if first_waiting_thread:
                        first_waiting_thread.text += '\n' + wait_thread.text
                        change_state(wait_thread, "close")
                    else:
                        # if first_waiting_thread removed, change target
                        first_waiting_thread = wait_thread

                if first_waiting_thread and len(wait_threads_delete_after) > 0:
                    # IF there's waiting thread & waiting threads(should be delete) > 0
                    print_log('log', 'waiting thread merged', f'\n{first_waiting_thread.text}')


                # Check reply text
                first_index_reply = prompt_thread_list[0].reply_text
                prompt_thread_list[0].print_thread_list()
                # print(first_index_reply)

                if first_index_reply != "":
                    self.prompt_done_signal.emit()

            # TTS THREAD
            if len(tts_thread_list) >= 1:
                # Start first thread if not running
                # for tts_thread in tts_thread_list:
                # Todo:20230830 tts thread check for loop

                if not tts_thread_list[0].isRunning() and tts_thread_list[0].state[0] == "init":
                    tts_thread_list[0].start()
                    print(f"start tts thread: [{tts_thread_list[0].text}]")

                tts_thread_list[0].print_thread_list()

                if tts_thread_list[0].state[0] == "close":
                    print("tts process all done: ", tts_thread_list[0].text, tts_thread_list[0].state[1])
                    # Remove current thraed
                    self.tts_play_done_signal.emit()

            # region MIC RECORDER & ADM
            if self.mic_thread.adm:
                if self.mic_thread.adm.selected_mic:
                    if self.mic_thread.adm.selected_mic.name:
                        if not self.mic_thread.device_name:
                            # print("assign first mic device name")
                            self.mic_thread.device_name = self.mic_thread.adm.selected_mic.name

                        if not self.mic_thread.isRunning():
                            # print_log("red", "Start Mic thread")
                            self.mic_thread.start()

            if self.sub_mic_thread.adm:
                if self.sub_mic_thread.adm.selected_sub_mic:
                    if self.sub_mic_thread.adm.selected_sub_mic.name:
                        if not self.sub_mic_thread.device_name:
                            # print("assign first sub mic device name")
                            self.sub_mic_thread.device_name = self.sub_mic_thread.adm.selected_sub_mic.name

                        if not self.sub_mic_thread.isRunning():
                            # print_log("red", "Start Sub Mic thread")
                            self.sub_mic_thread.start()
            # endregion MIC RECORDER & ADM

            time.sleep(0.3)

class PROMPTTHREAD(QThread):    # add whisper
    PromptDone = Signal(str, str)
    def __init__(self, parent, audio_file="", audio_length="", text="", logging=True):
        super().__init__(parent)
        self.parent = parent
        # Audio Input
        self.audio_file = audio_file
        self.audio_length = audio_length
        # STT generator
        self.stt = None

        # Text Input
        self.text = text

        # prompt generator
        self.gen = None
        self.character = self.parent.char_info_dict["character_name"]
        self.reply_text = ""

        self.state = ["",""]
        change_state(self, "init")
        self.logging = logging

    def run(self):
        if self.audio_file != '':
            # Speech To Text Generator
            self.stt = GeneratorSTT()
            change_state(self, "STT", "Transcribing")
            self.parent.load_audio_info()
            # print_log('red', 'stt_lang:', self.parent.audio_info_dict['stt_language'])
            self.text, _ = self.stt.speech_to_text(self.audio_file, self.parent.audio_info_dict['stt_language'])
            if self.text == "":
                self.stop()
                raise RuntimeError('STT result text is empty')
            else:
                # print(f'STT result: {self.text}')
                pass

        change_state(self, 'wait','Waiting send prompt')
        # Wait until this thread is top from list
        while True:
            if len(self.parent.prompt_thread_list) < 1:
                break
            if self.state[0] != 'wait':
                if self.state[0] == 'close':
                    print_log('warning', 'this thread is terminated', f'{self.text}')
                    self.stop()
                    return
                break
            # print_log("warning", self.state[0], self.state[1])
            time.sleep(0.3)
        self.gen = Generator()
        in_text = self.text
        change_state(self, "gen")

        tts_only = self.parent.chat_info_dict['tts_only']

        self.parent.load_other_info()  # Reload other settings, because it's not updating after changes
        self.reply_text = self.gen.generate(in_text,
                                            [self.parent.audio_info_dict, self.parent.char_info_dict,
                                             self.parent.prompt_info_dict, self.parent.chat_info_dict] ,
                                            tts_only=tts_only)

        if not self.reply_text:
            print_log('error','No reply text is Generated!', 'Make sure Language Model API URL is Valid')
            self.reply_text = 'No reply text is Generated! Make sure Language Model API URL is Valid'
            self.stop()
            raise RuntimeError('Make sure Language Model API URL is Valid')

        change_state(self, "check", "Check Command")
        # print("PromptThread created reply: ", self.reply_text, f"| text: {self.text}")
        cmd, value = self.gen.split_botcommand(self.reply_text)

        self.PromptDone.emit(cmd, value)
        change_state(self, "close")

    def remove_from_thread_list(self):
        self.parent.prompt_thread_list.remove(self)

    def stop(self):
        change_state(self, "close")
        self.remove_from_thread_list()

        self.quit()
        self.wait(5000)  # 5000ms = 5s

    def print_thread_list(self):
        if self.logging:
            print_thread_list("Prompt", self.parent.prompt_thread_list)

class TTSTHREAD(QThread):
    # TTSDone = Signal()
    def __init__(self, parent, text="", logging=True):
        super().__init__(parent)
        self.parent = parent
        self.gen = GeneratorTTS()
        self.text = text
        self.character = self.parent.audio_info_dict["tts_character"]

        self.state = ["",""]
        change_state(self, "init")
        self.logging = logging
    def run(self):
        self.gen.audio_dir = audio_cache_dir

        change_state(self, "gen", "Generating TTS")
        self.gen.speak_tts(text=self.text)

        print("tts wav file is generated: ", self.text, self.gen,
              f"Path[{self.gen.final_result_path}]")
        spk_device = self.parent.newAudDevice.selected_speaker
        spk_volume = self.parent.audio_info_dict['speaker_volume']

        # Init Spk Toggle
        self.gen.spk_toggle = self.parent.audio_info_dict['spk_toggle']

        change_state(self, "play", "Playing TTS")
        self.gen.play_by_bot(spk_device.name, spk_volume, quite_mode=False)
        change_state(self, "close")

    def remove_from_thread_list(self):
        self.parent.tts_thread_list.remove(self)

    def print_thread_list(self):
        if self.logging:
            print_thread_list("TTS/COMMAND", self.parent.tts_thread_list)

class COMMANDTHREAD(QThread):
    # CommandDone = Signal()
    def __init__(self, parent, cmd_type="", text="", logging=True):
        super().__init__(parent)
        self.parent = parent
        self.gen = BotCommand()
        self.cmd_type = cmd_type
        self.text = text

        # Assign values for bot_cmd
        self.character = parent.refresh_rvc_model()  # check using tts_char_name or not
        bot_cmd = self.gen
        bot_cmd.char_model_name = self.character
        bot_cmd.index_rate = parent.command_info_dict['rvc_index_rate']
        bot_cmd.fast_search = parent.command_info_dict['rvc_fast_search']
        bot_cmd.auto_pitch_bool = parent.command_info_dict['rvc_auto_pitch']
        bot_cmd.gender_type = parent.command_info_dict['rvc_gender']
        bot_cmd.pitch = parent.command_info_dict['rvc_pitch']

        bot_cmd.overwrite_final = parent.command_info_dict['rvc_overwrite_final']
        bot_cmd.main_gain = parent.command_info_dict['rvc_main_vocal']
        bot_cmd.backup_gain = parent.command_info_dict['rvc_backup_vocal']
        bot_cmd.music_gain = parent.command_info_dict['rvc_music']
        bot_cmd.master_gain = parent.command_info_dict['rvc_master_gain']
        bot_cmd.device_name = self.parent.newAudDevice.selected_speaker

        self.state = ["",""]
        change_state(self, "init")
        self.logging = logging

    def run(self):
        bot_cmd = self.gen

        change_state(self, "gen", f"Generating [{self.cmd_type}]")
        bot_cmd.do_command(self.cmd_type, self.text)

        print("RVC wav file is generated: ", self.text, self.gen,
              f"Path[{self.gen.final_result_path}]")
        spk_device = self.parent.newAudDevice.selected_speaker
        spk_volume = self.parent.audio_info_dict['speaker_volume']

        # Init Spk Toggle
        self.gen.spk_toggle = self.parent.audio_info_dict['spk_toggle']

        change_state(self, "play", f"Doing [{self.cmd_type}]")
        self.gen.play_by_bot(spk_device.name, spk_volume, quite_mode=False)
        change_state(self, "close")

    def remove_from_thread_list(self):
        self.parent.tts_thread_list.remove(self)

    def print_thread_list(self):
        if self.logging:
            print_thread_list("TTS/COMMAND", self.parent.tts_thread_list)

def change_state(thread_self, state_code, custom_state=""):
    """
    Change State of processings (Prompt/TTS/Command..)
    Args:
        thread_self: thread itself (:py:class:`QThread`)
        state_code: ['init','gen','play','close'] :py:class:`str`
        custom_state: custom print :py:class:`str` of state
    """
    final_state = None
    _state_to_print = None
    if custom_state:
        _state_to_print = custom_state
    else:
        if state_code == 'init':
            _state_to_print = 'Initializing'
        elif state_code == 'gen':
            _state_to_print = 'Generating'
        elif state_code == 'play':
            _state_to_print = 'Playing'
        elif state_code == 'close':
            _state_to_print = 'Closing'
    final_state = [state_code, _state_to_print]

    thread_self.state = final_state
    thread_self.parent.update_table_signal.emit()

def print_thread_list(list_type_name, list):
    thread_logging_str = f"==================== {list_type_name} Thread List ===================="

    print("\033[32m" + thread_logging_str + "\033[0m")
    for i, qthread in enumerate(list):
        _class_type = type(qthread.gen).__name__  # get class of gen [Generator/TTS/BotCommand]
        if _class_type == "Generator":
            _msg = f"QThread ({i}): [{qthread.text}] | State: {qthread.state[1]}"
        elif _class_type == "GeneratorTTS":
            _msg = f"QThread ({i}): [{qthread.text}] | State: {qthread.state[1]}"
        elif _class_type == "BotCommand":
            _msg = f"QThread ({i}): [{qthread.text}] | Command Type: {qthread.cmd_type}| State: {qthread.state[1]}"
        else:
            _msg = f"QThread ({i}) [{qthread.text}]"

        print(_msg)
    print("\033[32m" + thread_logging_str + "\033[0m")

#################################################################################################
# endregion [Thread Classes & Static Methods]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
