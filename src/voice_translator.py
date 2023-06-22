from datetime import datetime
from threading import Thread
from time import sleep

import wave
from os import getenv

import deepl
import googletrans
import keyboard
import pyaudio
import requests
from dotenv import load_dotenv

from modules.asr import speech_to_text
from voicevox import speak

# import urllib.request
from modules.translator import DoTranslate
from iso639 import languages

from MoeGoe.Main import *  # not sure preimport works

# LanguageModel
from LangAIComm import generate_reply

# Load Voice Settings
from setting_info import SettingInfo

if __name__ == '__main__':
    load_dotenv()

    USE_DEEPL = getenv('USE_DEEPL', 'False').lower() in ('true', '1', 't')
    DEEPL_AUTH_KEY = getenv('DEEPL_AUTH_KEY')

    MIC_ID = int(getenv('MICROPHONE_ID'))
    RECORD_KEY = getenv('MIC_RECORD_KEY')
    LOGGING = getenv('LOGGING', 'False').lower() in ('true', '1', 't')
    MIC_AUDIO_PATH = Path(__file__).resolve().parent / r'audio/mic.wav'
    CHUNK = 1024
    FORMAT = pyaudio.paInt16

    # print("loaded all")
    # delta_t = (datetime.utcnow() - start_time)
    # print(f"[{delta_t.total_seconds()}] sec")

    load_emote_index = 3


def loading_emote():
    global load_emote_index
    append_str = ''

    for i in range(load_emote_index):
        append_str += '.'

    for i in range(3 - load_emote_index):
        append_str += ' '

    if load_emote_index > 2:
        load_emote_index = 0
        # print(load_emote_index)
    else:
        # print(load_emote_index,end="")
        load_emote_index += 1

    return append_str


def voice_ready(ready_str):
    print(f"\r{ready_str}{loading_emote()}          ", end="")


def Do_Generate(eng_speech, speech_lang, settings_list: list = None):
    log_str = ""
    # Load Program Settings
    tts_settings, character_settings, other_settings = None, None, None

    if settings_list is None or len(settings_list) == 0:
        log_str = "[voice_translator/Do_Generate]: No loaded settings exist! loading them now..."
        settings_list = SettingInfo.load_all_settings()

    else:
        log_str = "[voice_translator/Do_Generate]: Using loaded program settings from main GUI"

    tts_settings = settings_list[0]
    character_settings = settings_list[1]
    other_settings = settings_list[2]

    if LOGGING:
        print(log_str)

    ai_model_language = other_settings["ai_model_language"]  # language that AI Model using ("pygmalion should communicate with  english")

    bot_reply = ""

    if eng_speech:
        if USE_DEEPL:
            translated_speech = translator.translate_text(eng_speech, target_lang=ai_model_language)
        else:
            translated_speech = DoTranslate(eng_speech, speech_lang, ai_model_language)
            # translated_speech = translator.translate(eng_speech, dest=tts_language).text

        if LOGGING:
            source_lang_name = languages.get(alpha2=speech_lang).name
            # print(f'{source_lang_name}: {eng_speech}')
            print(f'User: {translated_speech}')

        bot_reply = generate_reply(translated_speech, character_settings["character_name"])
        # bot_trans_speech = DoTranslate(bot_reply,'en',target_lang=tts_language)

        if LOGGING:
            print(f'Bot: {bot_reply}')

        # print("speak 함수 실행")

        # speak(bot_trans_speech, tts_language)
        # print("speak 함수 끝")
    else:
        # print('No speech detected.')
        print('목소리를 감지할수 없거나 알 수 없는 오류가 발생했습니다.')
        translated_speech = DoTranslate("목소리를 감지할수 없거나 알 수 없는 오류가 발생했습니다.", target_lang='ja')

    if bot_reply != "":
        speak(bot_reply, tts_settings, other_settings)


def on_press_key(_):
    voice_ready("녹음 버튼 누름")

    global frames, recording, stream
    if not recording:
        frames = []
        recording = True
        stream = p.open(format=FORMAT,
                        channels=MIC_CHANNELS,
                        rate=MIC_SAMPLING_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=MIC_ID)


def on_release_key(_):
    print("\n녹음 완료")
    global recording, stream
    recording = False
    stream.stop_stream()
    stream.close()
    stream = None

    # if empty audio file
    if not frames:
        print('No audio file to transcribe detected.')
        return

    # write microphone audio to file
    wf = wave.open(str(MIC_AUDIO_PATH), 'wb')
    wf.setnchannels(MIC_CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(MIC_SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    # print("음성인식 전")
    # transcribe audio
    try:
        eng_speech, speech_lang = speech_to_text(MIC_AUDIO_PATH, 'transcribe', 'any')
    except requests.exceptions.JSONDecodeError:
        print('Too many requests to process at once')
        return

    Do_Generate(eng_speech, speech_lang)


if __name__ == 'voice_translator':
    print()
    # now using class, so it's unnecessary
    # p = pyaudio.PyAudio()
    #
    # # get channels and sampling rate of mic
    # mic_info = p.get_device_info_by_index(MIC_ID)
    # MIC_CHANNELS = mic_info['maxInputChannels']
    # MIC_SAMPLING_RATE = int(mic_info['defaultSampleRate'])
    #
    # frames = []
    # recording = False
    # stream = None


class VoiceTranslator:
    def __init__(self):
        self.logging = True

    def generate(self, text, settings_list: list = None):
        from modules.translator import DoTranslate, detect_language
        log_str = ""
        # Load Program Settings
        tts_settings, character_settings, other_settings = None, None, None

        if settings_list is None or len(settings_list) == 0:
            log_str = "[VoiceTranslator.Generate]: No loaded settings exist! loading them now..."
            settings_list = SettingInfo.load_all_settings()

        else:
            log_str = "[VoiceTranslator.Generate]: Using loaded program settings from main GUI"

        tts_settings = settings_list[0]
        character_settings = settings_list[1]
        other_settings = settings_list[2]

        if self.logging:
            print(log_str)

        ai_model_language = other_settings["ai_model_language"]  # language that AI Model using ("pygmalion should communicate with  english")

        bot_reply = ""

        if text:
            speech_lang = detect_language(text)
            translated_speech = DoTranslate(text, speech_lang, ai_model_language)

            if self.logging:
                source_lang_name = languages.get(alpha2=speech_lang).name
                # print(f'{source_lang_name}: {eng_speech}')
                print(f'User: {translated_speech}')

            bot_reply = generate_reply(translated_speech, character_settings["character_name"])
            # bot_trans_speech = DoTranslate(bot_reply,'en',target_lang=tts_language)

            if self.logging:
                print(f'Bot: {bot_reply}')
        else:
            print('[VoiceTranslator.Generate] Error: text variable is None')
            return None    # failed

        if bot_reply == "":
            print('[VoiceTranslator.Generate] Error: text value is blank')
            return None    # failed

        # speak(bot_reply, tts_settings, other_settings)
        return bot_reply    # success


if __name__ == '__main__':
    # voiceTr = VoiceTranslator()
    # voiceTr.generate("기분이 어때?")
    # exit(0)

    p = pyaudio.PyAudio()

    # get channels and sampling rate of mic
    mic_info = p.get_device_info_by_index(MIC_ID)
    MIC_CHANNELS = mic_info['maxInputChannels']
    MIC_SAMPLING_RATE = int(mic_info['defaultSampleRate'])

    frames = []
    recording = False
    stream = None

    # Set DeepL or Google Translator
    if USE_DEEPL:
        translator = deepl.Translator(DEEPL_AUTH_KEY)
    else:
        translator = googletrans.Translator()

    keyboard.on_press_key(RECORD_KEY, on_press_key)
    keyboard.on_release_key(RECORD_KEY, on_release_key)

    try:
        while True:
            if recording and stream:
                data = stream.read(CHUNK)
                frames.append(data)
            elif not recording and not stream:
                sleep(0.5)
                voice_ready("record ready")

    except KeyboardInterrupt:
        print('Closing voice translator.')

