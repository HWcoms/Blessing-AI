import os
import sys
sys.path.append(os.path.dirname(__file__))  # prevent error when calling print_log from other python codes
from color_log import print_log

# Folders
module_dir = os.path.dirname(__file__)
src_dir = os.path.dirname(module_dir)
root_dir = os.path.dirname(src_dir)

# main.py [GUI]
audio_cache_dir = os.path.join(root_dir, 'cache', 'audio')
char_json_dir = os.path.join(root_dir, 'Models', 'Characters')  # LangAIComm

# main [MoeGoe]
tts_char_dir = os.path.join(root_dir, 'Models', 'Voice')    # main GUI

# page_massages
gui_cache_dir = os.path.join(root_dir, 'cache', 'gui')

# LangAIComm
character_chatlog_dir = os.path.join(root_dir, 'Models', 'ChatLog')

# pygame_mic
user_mic_cache_dir = os.path.join(root_dir, 'cache', 'user_mic')

# download_rvc_models [rvc_required_dir]
BASE_DIR = os.path.join(src_dir, 'Models', 'rvc_model')

# sing_command
rvc_required_dir = os.path.join(root_dir, 'Models', 'rvc_model')  # MDX, RVC Pretrained models
rvc_voice_dir = os.path.join(root_dir, 'Models', 'rvc_voice')  # Voice Models (pth, index)

rvc_cache_dir = os.path.join(root_dir, 'cache', 'rvc')
process_dir = os.path.join(rvc_cache_dir, "song_process")


def check_folder(folder_path):
    # CHECK VOICE CACHE FOLDER
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print_log("warning", "Created Necessary Folder!", folder_path)


def init_folders():
    for folder in [audio_cache_dir, tts_char_dir, gui_cache_dir,
                   character_chatlog_dir, user_mic_cache_dir, rvc_required_dir,
                   rvc_voice_dir, rvc_cache_dir, process_dir]:
        check_folder(folder)


if __name__ == '__main__':
    init_folders()
