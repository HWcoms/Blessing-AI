import json
from os import getenv
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

import requests
from MoeGoe.Main import speech_text
# discord bot feature
from discordbot import ExcuteDiscordWebhook
from dotenv import load_dotenv
# romaji to japanese
from modules.convert_roma_ja import english_to_katakana

from modules.audio_to_device import play_voice
from modules.translator import DoTranslate

load_dotenv()

# Audio devices
SPEAKERS_INPUT_ID = int(getenv('VOICEMEETER_INPUT_ID'))
APP_INPUT_ID = int(getenv('CABLE_INPUT_ID'))

audio_volume = 1

# Voicevox settings
BASE_URL = getenv('VOICEVOX_BASE_URL')
# BASE_URL = 'http://127.0.0.1:50021'
VOICE_ID = int(getenv('VOICE_ID'))
SPEED_SCALE = float(getenv('SPEED_SCALE'))
VOLUME_SCALE = float(getenv('VOLUME_SCALE'))
INTONATION_SCALE = float(getenv('INTONATION_SCALE'))
PRE_PHONEME_LENGTH = float(getenv('PRE_PHONEME_LENGTH'))
POST_PHONEME_LENGTH = float(getenv('POST_PHONEME_LENGTH'))

TTS_WAV_PATH = Path(__file__).resolve().parent.parent / r'audio\tts.wav'


def speak(sentence, language_code, character_name, tts_character_name, voice_id, voice_volume, use_d_bot):
    # print("번역전 텍스트: ", sentence)
    bot_trans_speech = DoTranslate(sentence, 'en', language_code)    # Translate reply
    if language_code == 'ja':
        bot_trans_speech = english_to_katakana(bot_trans_speech)            # romaji to japanese
    elif language_code == 'ko':
        bot_trans_speech = bot_trans_speech                                 # TODO: eng to korean
        voice_volume = voice_volume * 0.3

    # synthesize voice as wav file
    # speech_text("character_name", bot_trans_speech, language_code, voice_id, voice_volume)
    speech_text(tts_character_name, bot_trans_speech, language_code, voice_id, voice_volume)

    # play voice to app mic input and speakers/headphones
    threads = [Thread(target=play_voice, args=[APP_INPUT_ID]), Thread(target=play_voice, args=[SPEAKERS_INPUT_ID])]

    if use_d_bot:
        # Do translate to korean, if it's not 'ko'
        if language_code != 'ko':
            ko_sentence = DoTranslate(sentence, 'en', 'ko')
        else:
            ko_sentence = bot_trans_speech

        # SendDiscordMessage(ko_sentence)
        ExcuteDiscordWebhook(ko_sentence)

    [t.start() for t in threads]
    [t.join() for t in threads]


def speak_jp_VoiceVox(sentence):
    settings_json = read_text_file(Path(__file__).resolve().parent.parent.parent / r'Voice_Settings.txt')

    print("========TTS 설정=========")
    print("TTS 보이스 ID: ", settings_json["voice_id"])
    print("TTS 스피드: ", settings_json["voice_speed"])
    print("TTS 볼륨: ", settings_json["voice_volume"])
    print("INTONATION_SCALE: ", settings_json["intonation_scale"])
    print("PRE_PHONEME_LENGTH: ", settings_json["pre_phoneme_length"])
    print("POST_PHONEME_LENGTH: ", settings_json["post_phoneme_length"])
    print("====================\n")

    voice_Dyna_id = settings_json["voice_id"]  # id

    params_encoded = urlencode({'text': sentence, 'speaker': voice_Dyna_id})
    r = requests.post(f'{BASE_URL}/audio_query?{params_encoded}')

    if r.status_code == 404:
        print('Unable to reach Voicevox, ensure that it is running, or the VOICEVOX_BASE_URL variable is set correctly')
        return

    voicevox_query = r.json()

    voicevox_query['speedScale'] = settings_json["voice_speed"]
    voicevox_query['volumeScale'] = settings_json["voice_volume"]
    voicevox_query['intonationScale'] = settings_json["intonation_scale"]
    voicevox_query['prePhonemeLength'] = settings_json["pre_phoneme_length"]
    voicevox_query['postPhonemeLength'] = settings_json["post_phoneme_length"]

    # voicevox_query['speedScale'] = SPEED_SCALE
    # voicevox_query['volumeScale'] = VOLUME_SCALE
    # voicevox_query['intonationScale'] = INTONATION_SCALE
    # voicevox_query['prePhonemeLength'] = PRE_PHONEME_LENGTH
    # voicevox_query['postPhonemeLength'] = POST_PHONEME_LENGTH

    # synthesize voice as wav file

    params_encoded = urlencode({'speaker': voice_Dyna_id})
    r = requests.post(f'{BASE_URL}/synthesis?{params_encoded}', json=voicevox_query)

    with open(TTS_WAV_PATH, 'wb') as outfile:
        outfile.write(r.content)

    # play voice to app mic input and speakers/headphones
    threads = [Thread(target=play_voice, args=[APP_INPUT_ID]), Thread(target=play_voice, args=[SPEAKERS_INPUT_ID])]
    [t.start() for t in threads]
    [t.join() for t in threads]

    print("준비완료")


def read_text_file(filename):
    # 텍스트 파일 읽기
    with open(filename, 'r') as file:
        data = file.read()

    data = data.strip()

    # JSON 변환
    try:
        json_data = json.loads(data)
    except json.JSONDecodeError:
        print("Invalid JSON format in the text file.")
        return None

    return json_data


if __name__ == '__main__':
    # test if voicevox is up and running

    # print(load_tts_setting())
    print('Voicevox attempting to speak now...')
    # speak('むかしあるところに、ジャックという男の子がいました。ジャックはお母さんと一緒に住んでいました。','ja')
