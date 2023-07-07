import requests

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


def ExcuteDiscordWebhook(message, webhook_url, username, avatar):
    webhook_data['content'] = message
    webhook_data['username'] = username

    # print(webhook_url)

    if avatar is not None and avatar != "":
        webhook_data['avatar_url'] = avatar

    try:
        result = requests.post(webhook_url, json=webhook_data)
    except Exception as e:
        print_error("ExcuteDiscordWebhook", e)


def print_error(function_name: str, error: Exception):
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

    return base64_string


def show_base64_image(base64_str):
    import cv2      # noqa
    from PIL import Image
    from io import BytesIO
    import numpy

    img = Image.open(BytesIO(base64.b64decode(base64_str))).convert('RGB')

    # img_to_view = cv2.imread(img)
    img_to_view = numpy.array(img)  # noqa
    img_to_view = img_to_view[:, :, ::-1].copy()

    cv2.imshow('image', img_to_view)
    cv2.waitKey(0)

