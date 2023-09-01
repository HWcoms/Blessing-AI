import json
from pathlib import Path
import os
from modules.color_log import print_log

settings_folder = Path(__file__).resolve().parent.parent / 'settings'
gender_settings_dir = Path(__file__).resolve().parent.parent / 'cache' / 'rvc'


class SettingInfo:
    @staticmethod
    def load_all_settings():
        """
            [return]
            audio_settings
            character_settings
            prompt_settings
            other_settings
        """
        audio_settings = SettingInfo.load_audio_settings()
        character_settings = SettingInfo.load_character_settings()
        prompt_settings = SettingInfo.load_prompt_settings()
        other_settings = SettingInfo.load_other_settings()

        settings_list = [audio_settings, character_settings, prompt_settings, other_settings]
        return settings_list

    @staticmethod
    def load_audio_settings():
        settings_json = read_text_file(settings_folder / 'audio_settings.txt')
        return settings_json

    @staticmethod
    def load_character_settings():
        settings_json = read_text_file(settings_folder / 'character_settings.txt')
        return settings_json

    @staticmethod
    def load_other_settings():
        settings_json = read_text_file(settings_folder / 'other_settings.txt')
        return settings_json

    @staticmethod
    def load_prompt_settings():
        settings_json = read_text_file(settings_folder / 'prompt_settings.txt')
        return settings_json

    @staticmethod
    def load_command_settings():
        settings_json = read_text_file(settings_folder / 'command_settings.txt')
        return settings_json

    @staticmethod
    def get_chatlog_filename(character_name, full_path=False):
        from LangAIComm import check_chatlog
        return check_chatlog(character_name, full_path)

    @staticmethod
    def load_rvc_gender_settings():
        file_path = gender_settings_dir / 'rvc_gender_settings.txt'
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('{}')
            print_log("warning", "Created RVC Gender Setting File", f'[{file_path}]')

        settings_json = read_text_file(file_path)
        return settings_json

    # will be deprecated
    @staticmethod
    def load_settings():
        # Load Voice_Settings.txt
        settings_json = read_text_file(settings_folder / 'voice_settings.txt')

        return settings_json


def read_text_file(filename):
    # 텍스트 파일 읽기
    with open(filename, 'r', encoding='utf-8') as file:
        setting_data = file.read()

    setting_data = setting_data.strip()

    # JSON 변환
    try:
        json_data = json.loads(setting_data)
    except json.JSONDecodeError:
        print(
            "\033[31m" + "Invalid JSON format in the text file." + "\033[33m" + f" Please check the Syntax of setting file: '{filename}'" "\033[0m")
        return None

    return json_data


def update_json(key_str, data, filename, folderpath=settings_folder):
    fixed_file_name = folderpath / f'{filename}.txt'

    # Load the JSON file
    with open(fixed_file_name, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Split the key string into individual keys
    keys = key_str.split('.')

    # Traverse the JSON data to find the specified keys
    current_dict = json_data
    for key in keys[:-1]:
        if key not in current_dict:
            raise KeyError(f"[setting_info.update_json] Key '{key}' not found in JSON data. [{filename}]")
        current_dict = current_dict[key]

    # Update the value of the last key
    last_key = keys[-1]
    if last_key not in current_dict:
        raise KeyError(f"[setting_info.update_json] Key '{last_key}' not found in JSON data. [{filename}]")
    current_dict[last_key] = data

    # Save the updated JSON back to the file
    with open(fixed_file_name, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent="\t")


def add_item_json(key_str, data, filename, folderpath=settings_folder):
    file_path = folderpath / f'{filename}.txt'
    # Load the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Split the key string into individual keys
    keys = key_str.split('.')

    # Traverse the JSON data to find the specified keys
    current_dict = json_data
    for key in keys[:-1]:
        if key not in current_dict:
            current_dict[key] = {}  # Add a new empty dictionary if the key doesn't exist
        current_dict = current_dict[key]

    # Update the value of the last key or add a new key
    last_key = keys[-1]
    current_dict[last_key] = data

    # Save the updated JSON back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent="\t")


if __name__ == "__main__":
    print()
    print(SettingInfo.load_rvc_gender_settings())
    # Example usage
    # update_json('discord_bot', False, settings_folder / 'other_settings.txt')
