from datetime import datetime, timedelta
from threading import Thread
from time import sleep

load_ready = False
start_time = datetime.utcnow()

load_emote_index = 3

def loading_emote():
    global load_emote_index
    str = ''
    
    for i in range(load_emote_index):
        str += '.'
        
    for i in range(3-load_emote_index):
        str += ' '
    
    if(load_emote_index > 2):
        load_emote_index = 0
        # print(load_emote_index)
    else:
        # print(load_emote_index,end="")
        load_emote_index += 1
    
    return str  
        
def voice_ready(str):      
    print(f"\r{str}{loading_emote()}          ", end="")
    
def loading(str):
    while(load_ready == False):
        delta_t = (datetime.utcnow() - start_time)          
        print(f"\r{str}{loading_emote()} [{delta_t.total_seconds()} sec]          ", end="")
        sleep(0.05)
        
    print()
        

t_loading = Thread(target=loading, args=["Initiating"])
t_loading.start()


import wave
from os import getenv
from pathlib import Path

import deepl
import googletrans
import keyboard
import pyaudio
import requests
from dotenv import load_dotenv

from modules.asr import speech_to_text
from modules.tts import speak

# from iso639 import languages
# import urllib.request
# import json
from modules.translator import DoTranslate
from iso639 import languages

from MoeGoe.MoeGoe import * #not sure preimport works


load_dotenv()

USE_DEEPL = getenv('USE_DEEPL', 'False').lower() in ('true', '1', 't')
DEEPL_AUTH_KEY = getenv('DEEPL_AUTH_KEY')

MIC_ID = int(getenv('MICROPHONE_ID'))
RECORD_KEY = getenv('MIC_RECORD_KEY')
LOGGING = getenv('LOGGING', 'False').lower() in ('true', '1', 't')
MIC_AUDIO_PATH = Path(__file__).resolve().parent / r'audio/mic.wav'
CHUNK = 1024
FORMAT = pyaudio.paInt16

TARGET_LANGUAGE = getenv('TARGET_LANGUAGE_CODE')

def on_press_key(_):
    print("녹음 버튼 누름")
    
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
    print("녹음 완료")
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

    if eng_speech:
        if USE_DEEPL:
            translated_speech = translator.translate_text(eng_speech, target_lang=TARGET_LANGUAGE)
        else:
            translated_speech = DoTranslate(eng_speech, speech_lang)
            #translated_speech = translator.translate(eng_speech, dest=TARGET_LANGUAGE).text

        if LOGGING:
            source_lang_name = languages.get(alpha2=speech_lang).name
            print(f'{source_lang_name}: {eng_speech}')
            print(f'Translated: {translated_speech}')
        # print("speak 함수 실행")
        speak(translated_speech, TARGET_LANGUAGE)
        # print("speak 함수 끝")
        
    else:
        #print('No speech detected.')
        print('목소리를 감지할수 없거나 알 수 없는 오류가 발생했습니다.')
        translated_speech = DoTranslate("목소리를 감지할수 없거나 알 수 없는 오류가 발생했습니다.")
        speak(translated_speech, TARGET_LANGUAGE)
        

if __name__ == '__main__':
    load_ready = True
    
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
            else:
                sleep(0.5)
                voice_ready("record ready")
                
                    

    except KeyboardInterrupt:
        print('Closing voice translator.')

