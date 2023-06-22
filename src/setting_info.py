import json
from pathlib import Path

settings_folder = Path(__file__).resolve().parent.parent / 'settings'


class SettingInfo:
    @staticmethod
    def load_all_settings():
        """
            [return]
            tts_settings
            character_settings
            other_settings
        """
        tts_settings = SettingInfo.load_tts_settings()
        character_settings = SettingInfo.load_character_settings()
        other_settings = SettingInfo.load_other_settings()

        settings_list = [tts_settings, character_settings, other_settings]
        return settings_list

    @staticmethod
    def load_tts_settings():
        settings_json = read_text_file(settings_folder / 'TTS_Settings.txt')
        return settings_json

    @staticmethod
    def load_character_settings():
        settings_json = read_text_file(settings_folder / 'Character_Settings.txt')
        return settings_json

    @staticmethod
    def load_other_settings():
        settings_json = read_text_file(settings_folder / 'Other_Settings.txt')
        return settings_json

    # will be deprecated
    @staticmethod
    def load_settings():
        # Load Voice_Settings.txt
        settings_json = read_text_file(settings_folder / 'Voice_Settings.txt')

        return settings_json


def read_text_file(filename):
    # 텍스트 파일 읽기
    with open(filename, 'r') as file:
        setting_data = file.read()

    setting_data = setting_data.strip()

    # JSON 변환
    try:
        json_data = json.loads(setting_data)
    except json.JSONDecodeError:
        print("Invalid JSON format in the text file.")
        return None

    return json_data
