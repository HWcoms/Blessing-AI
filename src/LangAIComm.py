import base64
import json
import os
import urllib.parse

from setting_info import *

# Load ChatLog
from datetime import datetime
from os import getenv
from pathlib import Path

import requests
# Load Json from Png
from PIL import Image
from dateutil.parser import parse
import re
from dotenv import load_dotenv

load_dotenv()

# For local streaming, the websockets are hosted without ssl - http://
# HOST = getenv('TEXTGENERATION_URL')
# gen_request_url = f'{HOST}/api/v1/generate'
# view_request_url = f'{HOST}/api/v1/view'
# token_request_url = f'{HOST}/api/v1/token-count'

# Global endpoint vars
gen_url_endpoint = 'v1/generate'
view_url_endpoint = 'v1/view'
token_url_endpoint = 'v1/token-count'
token_request_url = None

trim_string = '\n'

character_name = None  # 'Kato Megumi'


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
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()

    data = data.strip()

    # JSON 변환
    try:
        json_data = json.loads(data)
    except json.JSONDecodeError:
        print("Invalid JSON format in the text file.")

        return None

    return json_data


def save_text_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            # print(f"File '{file_path}' saved successfully.")
    except Exception as e:
        print(f"An error occurred while saving the file: {str(e)}")


def count_tokens(text):
    request = {
        'prompt': text,
        'tokens': -1
    }
    global token_request_url
    if token_request_url is None:
        inner_settings_json = SettingInfo.load_prompt_settings()
        token_request_url = check_url(inner_settings_json["api_url"], token_url_endpoint)

    try:
        response = requests.post(token_request_url, json=request)

        if response.status_code == 200:
            result_tokens = response.json()['results'][0]['tokens']
            # print(request['prompt'])
            # print(result)
            return result_tokens
    except Exception as e:
        print("\033[31m" + f"Error [LangAIComm.count_tokens]: Failed to count tokens: {e}" + "\n\033[0m")
        return None


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

    result_dict = {"your_name": name1, "character_name": name2, "greeting": greeting, "context": context}

    # return name1, name2, greeting, context
    return result_dict


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


def load_chatlog(file_path):
    with open(file_path, 'r', encoding='utf8') as file:
        data = file.read()

    data = data.strip()

    return data


def run(prompt, name1):
    # settings_json = read_text_file(Path(__file__).resolve().parent.parent / r'Voice_Settings.txt')
    settings_json = SettingInfo.load_prompt_settings()
    gen_request_url = check_url(settings_json["api_url"], gen_url_endpoint)
    max_reply_token = settings_json["max_reply_token"]

    request = {
        "your_name": name1,
        'prompt': prompt,
        'max_new_tokens': max_reply_token,
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

    try:
        response = requests.post(gen_request_url, json=request)

        if response.status_code == 200:
            result_prompt = response.json()['results'][0]['text']
            # print(result)
            trimmed_string = trim_until_newline(result_prompt)
            return trimmed_string
        else:
            print(f"Error [LangAIComm.run]: failed to request generate_reply [status_code: {response.status_code}]")
            return None
    except Exception as e:
        print("\033[31m" + "Error [LangAIComm.run]: Failed to request" + "\n\033[33m" + f"▲ {e}" + "\033[0m")
        return None


def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return ""


def trim_until_newline(string):
    # string = string.decode()

    index = string.find("\ncoms")
    if index != -1:
        return string[:index]
    else:
        return string


def clean_lines(string):
    return string.replace('\n', ' ')


def check_url(base_url, endpoint):
    if base_url.endswith('/api'):
        merged_url = base_url + '/' + endpoint
    elif base_url.endswith('/api/'):
        merged_url = base_url + endpoint
    elif base_url.endswith('/'):
        merged_url = base_url + 'api/' + endpoint
    else:
        merged_url = base_url + '/api/' + endpoint

    return merged_url


## Get character json for GUI
def get_character_info(character_name):
    # Load Character
    character_json_name = character_name + '.json'
    character_image_name = character_name + '.png'
    json_filepath = get_character_file(character_json_name)
    image_filepath = get_character_file(character_image_name)

    char_dict = load_character(json_filepath)

    character_image = None
    if os.path.exists(image_filepath):
        print("\033[34m" + "Bot profile Image exists." + "\033[0m")
        character_image = image_filepath
    else:
        print(
            "\033[31m" + "Warning [LangAIComm.get_character_info]: " + "\033[33m" + "Bot profile Image does not exist." + "\033[0m")

    # Add image path to char_dict
    char_dict["character_image"] = character_image

    return char_dict


def get_chatlog_info(character_name):
    # Load ChatLog
    chatlog_file_path = check_chatlog(character_name)
    chat_str = load_chatlog(chatlog_file_path)
    return chat_str


## Generate
def generate_reply(string, character_name, max_prompt_token=2048, max_reply_token=200):
    # Define file name that contains prompt

    character_file_path = character_name + '.json'

    # Load voice_settings
    char_settings_json = SettingInfo.load_character_settings()

    # Load Character
    filename = get_character_file(character_file_path)
    char_dict = load_character(filename)

    # Load ChatLog
    chatlog_file_path = check_chatlog(character_name)
    chat_str = load_chatlog(chatlog_file_path)

    user_input = char_settings_json["your_name"] + ": " + string + "\n" + char_dict["character_name"] + ":"

    if chat_str.strip() == '':
        chat_str_prompt = user_input  # Chatlog is empty
    else:
        chat_str_prompt = chat_str + '\n' + user_input  # Chatlog is not empty

    # remove unecessary \n
    # trim_str = re.sub(r"\n(?![a-zA-Z])", "", chat_str)
    optimized_chat_str = optimize_tokens(char_dict["context"], chat_str_prompt, max_prompt_token - max_reply_token)
    # print(max_reply_token)
    if optimized_chat_str is None:
        print(
            "\033[31m" + "Error [LangAIComm.generate_reply]: Could not Optimize Chat log by Tokens" + "\033[0m")
        return None

    optimized_content = char_dict["context"] + optimized_chat_str

    # print(file_content, end='')
    try:
        result_text = run(optimized_content, char_settings_json["your_name"])

        if result_text == "" or result_text is None:
            print(
                "\033[31m" + "Error [LangAIComm.generate_reply]: No reply returned. nothing will be update to chat_log.txt" + "\033[0m")
            return None

        result_text = clean_lines(result_text)

        # ADD PREFIXS EVERY LINES IF 'user_input' HAS MULTIPLE LINES
        prefix_user_input = add_prefix_lines(string, char_settings_json["your_name"]) + "\n" + char_dict["character_name"] + ":"

        if chat_str.strip() == '':
            prefix_chat_str = prefix_user_input  # Chatlog is empty
        else:
            prefix_chat_str = chat_str + '\n' + prefix_user_input  # Chatlog is not empty

        save_text_file(chatlog_file_path, prefix_chat_str + result_text)
        # print(file_content + result_text)

        # remove blanks from left
        if result_text[0] == ' ':
            result_text = result_text.lstrip()

        return result_text
    except Exception as e:
        print("\033[31m" + f"Error [LangAIComm.generate_reply]: {e}" + "\033[0m")
        return None


def get_character_file(character_name):
    # Load Character
    this_dir = os.path.dirname(os.path.abspath(__file__))
    char_path = os.path.join(this_dir, "Models", "Characters")
    char_file_path = os.path.join(char_path, character_name)

    return char_file_path


def add_prefix_lines(string, prefix):
    lines = string.splitlines()
    prefixed_lines = [f'{prefix}: ' + line for line in lines]  # Add the prefix to each line
    result = '\n'.join(prefixed_lines)  # Join the lines back into a single string

    return result

def extract_date(string):
    # Parse the string into a datetime object.
    date_pattern = r"\d{8}"
    matches = re.findall(date_pattern, string)
    if matches:
        date_info = matches[0]
        # print("Date Info:", date_info)

        return date_info
    else:
        # print("No date found in the string.")
        return None


def check_chatlog(character_name, full_path=True):
    # Check Character's chat file exist
    this_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(this_dir, "Models", "ChatLog")

    latest_file_path = None
    latest_date = None

    # date_string = datetime.now().strftime("%Y%m%d")
    # print(date_string)
    for file in os.listdir(folder_path):
        is_date = extract_date(file)
        if is_date is not None and character_name.lower() in file.lower():
            file_date = datetime.strptime(is_date, "%Y%m%d")
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file_path = os.path.join(folder_path, file)

    if latest_file_path is not None:
        if not full_path:
            return os.path.basename(latest_file_path)

        return latest_file_path

    if not full_path:
        print(
            "\033[31m" + "Error [LangAIComm.check_chatlog]: There's No ChatLog file to load only name.\nPlease use default [full_path] argument!" + "\033[0m")
        return None

    # if file doesn't exist.
    date_string = datetime.now().strftime("%Y%m%d")
    new_file_name = f'{character_name} {date_string}.txt'
    new_file_path = os.path.join(folder_path, new_file_name)

    try:
        with open(new_file_path, 'w') as f:
            print('Could not find any Chat log... Creating New one! ' + '\033[34m' + f"[{new_file_name}]" + '\033[0m')
            return new_file_path
    except FileNotFoundError:
        print('\033[31m' + "Error: Can't make chat log file!" + '\033[0m')
        return None


def optimize_tokens(context, dialogs, token_limit):
    global token_request_url

    full_text = context + dialogs
    opt_dialogs = ""
    # return count_tokens(full_text)
    full_text_tokens = count_tokens(full_text)

    if full_text_tokens is None:
        print(
            "\033[31m" + "Error [LangAIComm.optimize_tokens]: Failed to count tokens, exiting function" + "\n\033[0m")

        token_request_url = None
        return None

    if full_text_tokens > token_limit:
        # print("token too long: ", full_text_tokens)
        print(
            "\033[34m" + "[LangAIComm.optimize_tokens]: Requested Token is too long, Please consider make new chat log: " + "\033[33m"
            + f"{full_text_tokens} (token counts)" + "\033[0m")

        lines = dialogs.splitlines()[1:]
        opt_dialogs = '\n'.join(lines)
        return optimize_tokens(context, opt_dialogs, token_limit)
    else:
        # print("optimized text")
        token_request_url = None

        return dialogs


# Example usage
if __name__ == '__main__':
    print(generate_reply("I'm HWcoms", "Kato Megumi"))

    # settings_json = SettingInfo.load_prompt_settings()
    # print(settings_json)
    # gen_request_url = check_url(settings_json["api_url"], gen_url_endpoint)
    # print(gen_request_url)

    # print(run("hello", "coms"))

    # print(get_character_name())
    # print(count_tokens(context))
    # print(get_chatlog_info("Kato Megumi"))
    # print(count_tokens(char_data))
    # print(optimize_tokens(char_data, chat_log_string, 843+50))
