import time
from os import getenv
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from .audio_to_device import play_voice
from MoeGoe.MoeGoe import speech_text

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

def speak_jp(sentence):
    id, fls = read_numbers( Path(__file__).resolve().parent.parent / r'Voice_Settings.txt')        
    
    # print("========TTS 설정=========")
    # print("TTS 보이스 ID: ", id)
    # print("TTS 스피드: ", fls[0])
    # print("TTS 볼륨: ", fls[1])
    # print("INTONATION_SCALE: ", fls[2])
    # print("PRE_PHONEME_LENGTH: ", fls[3])
    # print("POST_PHONEME_LENGTH: ", fls[4])
    # print("====================\n")
    
    speaker_id = 0#id
    
    audio_volume = fls[1]
    
    # synthesize voice as wav file
    speech_text(sentence, speaker_id, audio_volume)

    # play voice to app mic input and speakers/headphones
    threads = [Thread(target=play_voice, args=[APP_INPUT_ID]), Thread(target=play_voice, args=[SPEAKERS_INPUT_ID])]
    [t.start() for t in threads]
    [t.join() for t in threads]
    
    


def speak_jp_VoiceVox(sentence):
              
    # generate initial query
    
    # with open('C:/Users/HWcoms/LanguageLeapAI/src/Voice_Settings.txt', 'r') as file:
    #     line = file.readline().strip()
    #     number = int(line)
    
    
    
    
    
    id, fls = read_numbers('C:/Users/HWcoms/LanguageLeapAI/src/Voice_Settings.txt')        
    
    print("========TTS 설정=========")
    print("TTS 보이스 ID: ", id)
    print("TTS 스피드: ", fls[0])
    print("TTS 볼륨: ", fls[1])
    print("INTONATION_SCALE: ", fls[2])
    print("PRE_PHONEME_LENGTH: ", fls[3])
    print("POST_PHONEME_LENGTH: ", fls[4])
    print("====================\n")
    
    voice_Dyna_id = id
    
    params_encoded = urlencode({'text': sentence, 'speaker': voice_Dyna_id})
    r = requests.post(f'{BASE_URL}/audio_query?{params_encoded}')

    if r.status_code == 404:
        print('Unable to reach Voicevox, ensure that it is running, or the VOICEVOX_BASE_URL variable is set correctly')
        return

    voicevox_query = r.json()
    voicevox_query['speedScale'] = fls[0]
    voicevox_query['volumeScale'] = fls[1]
    voicevox_query['intonationScale'] = fls[2]
    voicevox_query['prePhonemeLength'] = fls[3]
    voicevox_query['postPhonemeLength'] = fls[4]
    
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


def read_numbers(filename):
    with open(filename, 'r') as file:
        numbers = []
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Ignore comments and blank lines
            try:
                number = int(line) if '.' not in line else float(line)
                numbers.append(number)
                # print(number)
            except ValueError:
                pass  # Ignore lines that cannot be converted to numbers
            if len(numbers) == 6:
                break
        # if len(numbers) != 6:
        #     raise ValueError("File must contain one integer and five floats")
        x = numbers[0]
        y = numbers[1:]
        return x, y

if __name__ == '__main__':
    # test if voicevox is up and running
    print('Voicevox attempting to speak now...')
    speak_jp('むかしあるところに、ジャックという男の子がいました。ジャックはお母さんと一緒に住んでいました。')
