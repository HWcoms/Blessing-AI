import base64
import json
import os
# Load ChatLog
from datetime import datetime
from os import getenv
from pathlib import Path

import requests
# Load Json from Png
from PIL import Image
from dateutil.parser import parse
from dotenv import load_dotenv

load_dotenv()

# For local streaming, the websockets are hosted without ssl - http://
HOST = getenv('TEXTGENERATION_URL')
gen_request_url = f'{HOST}/api/v1/generate'
view_request_url = f'{HOST}/api/v1/view'
token_request_url = f'{HOST}/api/v1/token-count'

trim_string = '\n'

character_name = 'Kato Megumi'


## load voice_settings.txt

def load_png_character(filename):
    im = Image.open(filename)
    im.load()  # Needed only for .png EXIF data (see citation above)
    str_info = im.info['chara']
    decoded_string = base64.b64decode(str_info)
    _json = json.loads(decoded_string)
    _json = {"char_name": _json['name'], "char_persona": _json['description'], "char_greeting": _json["first_mes"],
             "example_dialogue": _json['mes_example'], "world_scenario": _json['scenario']}
    _json = json.dumps(_json)
    json_file = _json if type(_json) == str else _json.decode('utf-8')
    return json_file


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


def count_tokens(text):
    request = {
        'prompt': text,
        'tokens': -1
    }

    response = requests.post(token_request_url, json=request)

    if response.status_code == 200:
        result_tokens = response.json()['results'][0]['tokens']
        # print(request['prompt'])
        # print(result)
        return result_tokens


def load_character(filepath):
    # shared.character = character
    context = greeting = turn_template = ""
    greeting_field = 'greeting'
    # picture = None

    file_extension = os.path.splitext(filepath)[1][1:]
    file_contents = None
    data = None  # dict

    if file_extension == 'png':
        file_contents = load_png_character(filepath)
    elif file_extension == 'json':
        file_contents = open(filepath, 'r', encoding='utf-8').read()

    data = json.loads(file_contents)

    name2 = data['name'] if 'name' in data else data['char_name']
    if 'your_name' in data and data['your_name'] != '':
        name1 = data['your_name']
    else:
        name1 = "You"
    for field in ['context', 'first_mes', 'greeting', 'example_dialogue', 'mes_example', 'char_persona', 'description',
                  'char_greeting', 'scenario', 'world_scenario']:
        if field in data:
            data[field] = replace_character_names(data[field], name1, name2)

    if 'context' in data:
        context = data['context']
        context = context.strip() + '\n\n'
    elif "char_persona" in data:
        context = build_pygmalion_style_context(data)
        greeting_field = 'char_greeting'

    if 'example_dialogue' in data:
        context += f"{data['example_dialogue'].strip()}\n"

    if greeting_field in data:
        greeting = data[greeting_field]

    if 'turn_template' in data:
        turn_template = data['turn_template']

    return name1, name2, greeting, context


def replace_character_names(text, name1, name2):
    text = text.replace('{{user}}', name1).replace('{{char}}', name2)
    return text.replace('<USER>', name1).replace('<BOT>', name2)


def build_pygmalion_style_context(data):
    context = ""
    if 'char_persona' in data and data['char_persona'] != '':
        context += f"{data['char_name']}'s Persona: {data['char_persona']}\n"

    if 'world_scenario' in data and data['world_scenario'] != '':
        context += f"Scenario: {data['world_scenario']}\n"

    context = f"{context.strip()}\n<START>\n"
    return context


def run(prompt, name1):
    settings_json = read_text_file(Path(__file__).resolve().parent.parent / r'Voice_Settings.txt')
    max_token = settings_json["max_token"]

    request = {
        "your_name": name1,
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

    response = requests.post(gen_request_url, json=request)

    if response.status_code == 200:
        result_prompt = response.json()['results'][0]['text']
        # print(result)
        trimmed_string = trim_until_newline(result_prompt)
        return trimmed_string


def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return ""


def save_text_file(file_path, content):
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
    # Define file name that contains prompt
    character_file_path = character_name + '.json'

    chatlog_file_path = check_chatlog(character_name)

    # Load Character
    filename = get_character_file(character_file_path)
    name1, name2, greeting, context = load_character(filename)

    user_input = name1 + ": " + string + "\n" + name2 + ":"

    # Load ChatLog
    # this_dir = os.path.dirname(os.path.abspath(__file__))
    # chatLog_path = os.path.join(this_dir,"characters","ChatLog")
    # file_path = os.path.join(chatLog_path, file_name)

    file_content = context + user_input
    # print(file_content, end='')

    result_text = run(file_content, name1)
    result_text = clean_lines(result_text)
    # # print(result_text)

    # # save_textfile(file_path, file_content + result_text)

    return result_text


def get_character_file(character_name):
    # Load Character
    this_dir = os.path.dirname(os.path.abspath(__file__))
    char_path = os.path.join(this_dir, "Models", "Characters")
    char_file_path = os.path.join(char_path, character_name)

    return char_file_path


def extract_date(string, fuzzy=False):
    """
     Return whether the string can be interpreted as a date.

     :param string: str, string to check for date
     :param fuzzy: bool, ignore unknown tokens in string if True
     :return: bool, True if string can be interpreted as a date, False otherwise
     """
    # Split the string into words.
    words = string.split()

    # Check if any of the words are date formats.
    for word in words:
        try:
            parse(word, fuzzy=fuzzy)
            return word
        except ValueError:
            pass

    return None


def check_chatlog(character_name):
    # Check Character's chat file exist
    this_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(this_dir, "Models", "ChatLog")

    for file in os.listdir(folder_path):

        is_date = extract_date(file)
        if is_date is not None and character_name in file:
            return os.path.join(folder_path, file)
    return None

    # date_string = datetime.now().strftime("%Y%m%d")
    # print(date_string)


# Example usage
if __name__ == '__main__':
    # print(generate_reply ("what is your name??"))
    # print(HOST)

    # print(count_tokens(context))
    # result = check_chatlog("kato megumi")
    # date_string = datetime.now().strftime("%Y%m%d")
    # print(date_string)
    print(extract_date("kato megumi 20230505"))
