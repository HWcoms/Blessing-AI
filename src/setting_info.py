import json
from pathlib import Path


class SettingInfo:
    @staticmethod
    def load_settings():
        # Load Voice_Settings.txt
        settings_json = read_text_file(Path(__file__).resolve().parent.parent / r'Voice_Settings.txt')

        # character_name = settings_json["character_name"]
        # tts_character_name = settings_json["tts_character_name"]
        # tts_language = settings_json["tts_language"]
        # voice_id = settings_json["voice_id"]  # id
        # voice_volume = settings_json["voice_volume"]
        # USE_D_BOT = settings_json["discord_bot"]  # DISCORD BOT

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
