from pathlib import Path
import requests
from os import getenv
from dotenv import load_dotenv

import json


load_dotenv()

# For local streaming, the websockets are hosted without ssl - http://
HOST = getenv('TEXTGENERATION_URL')
URI = f'{HOST}/api/v1/generate'
URL = f'{HOST}/api/v1/view'

trim_string = '\n'


## load voice_settings.txt

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


def run(prompt):
     settings_json = read_text_file( Path(__file__).resolve().parent.parent / r'Voice_Settings.txt')
     max_token = settings_json["max_token"]
     
     request = {
          "your_name": "coms",
          'prompt': prompt,
          'max_new_tokens': max_token,
          'do_sample': True,
          'temperature': 0.72,
          'top_p': 0.73,
          'typical_p': 1,
          'repetition_penalty': 1.17,
          'top_k': 0,
          'min_length': 0,
          'no_repeat_ngram_size': 0,
          'num_beams': 1,
          'penalty_alpha': 0,
          'length_penalty': 1,
          'early_stopping': False,
          'seed': -1,
          'add_bos_token': True,
          'truncation_length': 2048,
          'ban_eos_token': False,
          'skip_special_tokens': True,
          'stopping_strings': ["\ncoms:"]
     }
     # request['prompt'] = request['prompt'].encode('utf-8').decode('utf-8') #making sure to en/decode as utf-8 - sometimes prompt get changed to symbols
     request['prompt'] = request['prompt'].strip()
     
     response = requests.post(URI, json=request)

     if response.status_code == 200:
          result = response.json()['results'][0]['text']
          # print(result)
          trimmed_string = trim_until_newline(result)
          return trimmed_string

def load_textfile(file_path):
     try:
          with open(file_path, 'r', encoding='utf-8') as file:
               content = file.read()
               return content
     except FileNotFoundError:
          print(f"File '{file_path}' not found.")
          return ""

def save_textfile(file_path, content):
     try:
          with open(file_path, 'w', encoding='utf-8') as file:
               file.write(content)
               # print(f"File '{file_path}' saved successfully.")
     except Exception as e:
          print(f"An error occurred while saving the file: {str(e)}")


def trim_until_newline(string):
     # string = string.decode()
     
     index = string.find("\ncoms")
     if index != -1:
          return string[:index]
     else:
          return string

def clean_lines(string):
     return string.replace('\n', ' ')

## Generate
def generate_reply(string):
     user_input = "coms: " + string + "\nKato Megumi:"
     
     file_path = 'C:/Users/HWcoms/Downloads/temp_megumi_prompt_05142037.txt'  # Replace with the actual file path
     file_content = load_textfile(file_path)
     file_content = file_content + "\n" + user_input
     # print(file_content, end='')
     
     result_text = run(file_content)
     result_text = clean_lines(result_text)
     # print(result_text)
     
     save_textfile(file_path, file_content + result_text)
     
     return result_text 


# Example usage
if __name__ == '__main__':
     print(generate_reply ("what is your name??"))
     print(HOST)