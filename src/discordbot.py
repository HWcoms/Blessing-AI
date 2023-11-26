import requests
from urllib.parse import urlparse
import os

payload = {
    'content': "silent request post without running bot in background",
    'flags': 4096
}


def SendDiscordMessage(message, bot_id, channel_id):
    payload['content'] = message

    header = {
        'authorization': 'Bot ' + bot_id
    }

    dsend_message_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"

    try:
        result = requests.post(dsend_message_url, data=payload, headers=header)
        return result
    except Exception as e:
        print_error("ExcuteDiscordWebhook", e)


# endregion

# region WEBHOOK MESSAGE
webhook_data = {
    "content": "message content",
    "username": "username",
    "avatar_url": "",
    'flags': 4096
}


def ModifyDiscordWebhook(webhook_url, username=None, avatar=None):
    mod_webhook_data = {}

    if username and username != "":
        mod_webhook_data['name'] = username

    if avatar and avatar != "":
        mod_webhook_data['avatar'] = avatar

    try:
        result = requests.patch(webhook_url, json=mod_webhook_data)
        return result

    except Exception as e:
        print_error("ModifyDiscordWebhook", e)


def ExcuteDiscordWebhook(message, webhook_url, username, avatar=None):
    webhook_data['content'] = message

    # Need this line because this method send request before changing webhook's 'name' property
    webhook_data['username'] = username
    # webhook_data['avatar'] = avatar

    # CHECK URL TYPE [data: or http:]
    # ////////////////////////////////////////////////////////
    if avatar and avatar != "":
        url_type = check_url_type(avatar)
        _final_url = None

        if url_type == 'data_url':
            webhook_data['avatar'] = avatar
            _final_url = avatar
            print(f'data uri: {avatar[:70]}...')
        elif url_type == 'file_url':
            base64_url = image_to_base64(avatar)
            webhook_data['avatar'] = base64_url
            _final_url = base64_url
        elif url_type == 'internet_url':
            webhook_data['avatar_url'] = avatar
            _final_url = avatar

        if url_type == 'unknown':
            print_error("ExcuteDiscordWebhook", f"Could not get type of url: {avatar}")
        elif not url_type == 'internet_url':
            webhook_data['avatar_url'] = None
            ret = ModifyDiscordWebhook(webhook_url, username, _final_url)

            _mod_avatar = ret.json()['avatar']
            if _mod_avatar:
                print("Modifying Discord webhook:", _mod_avatar)
            else:
                print_error("ModifyDiscordWebhook", 'moded avatar is None')

        if _final_url:
            print("avatar url: ", _final_url[:70])
        print("avatar url type: ", url_type)

    # ////////////////////////////////////////////////////////
    # CHECK URL TYPE [data: or http:]

    # print(webhook_data)

    try:
        result = requests.post(webhook_url, json=webhook_data)
        return result

    except Exception as e:
        print_error("ExcuteDiscordWebhook", e)


def print_error(function_name: str, error: Exception | str):
    print("\033[31m" + f"Error [discordbot.{function_name}]: " + "\033[33m" + f"{error}" + "\n\033[0m")


# endregion

def image_to_base64(path_str):
    from pathlib import Path
    import base64

    _image_path = Path(path_str)
    base64_string = None

    try:
        with open(_image_path, 'rb') as img:
            base64_string = base64.b64encode(img.read())
    except Exception as e:
        print("\033[31m" + f"Error [discordbot.image_to_base64]: Failed to convert Image to base64: {e}" + "\n\033[0m")

    base64_utf8_str = base64_string.decode('utf-8')
    _, ext = os.path.splitext(path_str)
    ext = ext[1:]
    # print(f"{_}, {ext}")

    dataurl = f'data:image/{ext};base64,{base64_utf8_str}'  # no need to match file extension. it works anyways (jpg, png tested)

    return dataurl


def show_base64_image(base64_dataurl):
    import cv2  # noqa
    from PIL import Image
    from io import BytesIO
    import numpy

    import re

    match = re.search(r'base64,([^"]+)', base64_dataurl)
    if match:
        base64_str = match.group(1)
    else:
        return None

    img = Image.open(BytesIO(base64.b64decode(base64_str))).convert('RGB')

    # img_to_view = cv2.imread(img)
    img_to_view = numpy.array(img)  # noqa
    img_to_view = img_to_view[:, :, ::-1].copy()

    cv2.imshow('image', img_to_view)
    cv2.waitKey(0)


def check_url_type(url_img):
    """
    This method checks the given string to determine its URL type.
    It returns one of the following strings: 'internet_url', 'data_url', 'file_url', 'unknown'

    :param url_img: online url or base64 (:py:class:`string`)
    :returns: 'internet_url' | 'data_url' | 'file_url' | 'unknown' (:py:class:`string`)
    """

    parsed_url = urlparse(url_img)
    if parsed_url.scheme == 'data':
        return 'data_url'
    elif parsed_url.scheme in ['http', 'https']:
        return 'internet_url'
    elif os.path.isfile(url_img):
        return 'file_url'
    else:
        return 'unknown'


if __name__ == "__main__":
    print()

    # avatar base64 test
    from pathlib import Path
    import base64
    from setting_info import SettingInfo
    settings_json = SettingInfo.load_other_settings()

    # pf_image_base64 = r"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"

    pf_image_file = r"C:\Users\HWcoms\Downloads\megumi.jpg"

    # pf_image_file = r"C:\Users\HWcoms\Downloads\d1520f9832eb84bb7c7b4db2766ad70962d234a79f211c5d243b90176cfbd04d.png"

    base64_result_image = image_to_base64(pf_image_file)
    # pf_image_file = "asdfasdf"
    show_base64_image(base64_result_image)

    # ExcuteDiscordWebhook(message="patch profile image with file path",
    #                      webhook_url=settings_json['discord_webhook_url'],
    #                      username="test_",
    #                      avatar=pf_image_file)
