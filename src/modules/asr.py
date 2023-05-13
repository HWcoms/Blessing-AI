from os import getenv
from pathlib import Path

import requests
from dotenv import load_dotenv

import json
import whisper
from faster_whisper import WhisperModel

load_dotenv()

# BASE_URL = getenv('WHISPER_BASE_URL')
# REQUEST_TIMEOUT = int(getenv('REQUEST_TIMEOUT'))
SAMPLE_JP_FILEPATH = Path(__file__).resolve().parent.parent / r'audio\samples\japanese_speech_sample.wav'
SAMPLE_EN_FILEPATH = Path(__file__).resolve().parent.parent / r'audio\samples\english_speech_sample.wav'


#whisper
# WHISPER_MODEL = 'base'  #model
# model = whisper.load_model(WHISPER_MODEL)     #original whisper

# Faster whistper
module_folder_path = Path(__file__).resolve().parent
whisper_small_ct2_path = str(module_folder_path / '..' / 'whisper-small-ct2')
whisper_large_v2_path = str(module_folder_path / '..' / 'whisper-large-v2-ct2')

WHISPER_MODEL = whisper_large_v2_path
model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")

def whisper_process(audio_data, tsk, lang):
    temp_path = r"{}".format(audio_data)
    # print("음성인식 시작")
    if tsk == 'transcribe':
#       audio_data.save(TRANSCRIBE_FILENAME)
        if(lang == 'any'):
            print("SubTitle Mode: any language")
            # result = model.transcribe(temp_path, task=tsk, fp16=False)
            result, info = model.transcribe(temp_path)
        else:   
            print("Voice Mode: ", lang)   
            # result = model.transcribe(temp_path, language=lang, task=tsk, fp16=False)
            result, info = model.transcribe(temp_path, language=lang)

        result = concatenate_strings(result)
    #     print("음성인식 끝")
        return result, info

    elif tsk == 'translate':
#       audio_data.save(TRANSLATE_FILENAME)
      result = model.translate(temp_path, language='ja', task='translate', fp16=False)
      return json.dumps(result)
    
    else:
      return 'Record not found', 400
  
def speech_to_text(filepath, task, language):
    try:
        result, lang_info = whisper_process(filepath, task, language)

    except Exception as e:
        print(f'An unknown error has occurred: {e}')
        return None

    # json_result = json.loads(result)
    # print(json_result['text'].strip())

    # return json_result['text'].strip(), json_result['language'].strip()
    return result, lang_info.language

def concatenate_strings(results):
    concatenated_string = ""
    for segment in results:
        # print(segment)
        concatenated_string += segment.text.strip() + " "
    return concatenated_string

# def speech_to_text(filepath, task, language, mode):
#     try:
#         with open(filepath, 'rb') as infile:
#             files = {'audio_file': infile}
#             r = requests.post(f'{BASE_URL}/asr?task={task}&language={language}&output=json',
#                               files=files,
#                               timeout=REQUEST_TIMEOUT)

#         if r.status_code == 404:
#             print('Unable to reach Whisper, ensure that it is running, or the WHISPER_BASE_URL variable is set correctly')
#             return None

#     except requests.exceptions.Timeout:
#         print('Request timeout')
#         return None

#     except Exception as e:
#         print(f'An unknown error has occurred: {e}')
#         return None

#     return r.json()['text'].strip()



if __name__ == '__main__':
    # test if whisper is up and running
    print('Testing Whisper on English speech sample.')
    print(f'Actual audio: Oh. Honestly, I could not be bothered to play this game to full completion.'
          f'The narrator is obnoxious and unfunny, with his humor and dialogue proving to be more irritating than '
          f"entertaining.\nWhisper audio: {speech_to_text(SAMPLE_EN_FILEPATH, 'transcribe', 'en')}\n")

    print('Testing Whisper on Japanese speech sample.')
    print(f'Actual translation: How is this dress? It suits you very well.\n'
          f"Whisper translation: {speech_to_text(SAMPLE_JP_FILEPATH, 'translate', 'ja')}")
