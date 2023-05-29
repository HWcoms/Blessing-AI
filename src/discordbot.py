from os import getenv

import requests
from dotenv import load_dotenv

load_dotenv()

# region BOT MESSAGE
BOT_TOKEN = getenv('D_BOT_TOKEN')  # Discord Bot Token
CHANNEL_ID = int(getenv('D_CHANNEL_ID'))  # Discord Text Channel

# CHANNEL_ID =           #2nd channel to test

dsend_message_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"

payload = {
    'content': "silent request post without running bot in background",
    'flags': 4096
}

header = {
    'authorization': 'Bot ' + BOT_TOKEN
}


def SendDiscordMessage(message):
    payload['content'] = message

    r = requests.post(dsend_message_url, data=payload, headers=header)


# SendDiscordMessage("called")
# print(payload['content'])

# endregion

# region WEBHOOK MESSAGE
WEBHOOK_URL = getenv('D_WEBHOOK')  # Discord Webhook Url
wh_username = getenv('D_WEBHOOK_USERNAME')
wh_avatar = getenv('D_WEBHOOK_AVATAR')

webhook_data = {
    "content": "message content",
    "username": "username",
    "avatar_url": "",
    'flags': 4096
}


def ExcuteDiscordWebhook(message, username=wh_username, avatar=wh_avatar):
    webhook_data['content'] = message
    webhook_data['username'] = username
    webhook_data['avatar_url'] = avatar

    result = requests.post(WEBHOOK_URL, json=webhook_data)

# ExcuteDiscordWebhook("called")

# endregion
