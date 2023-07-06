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

# # region WEBHOOK MESSAGE
# WEBHOOK_URL = getenv('D_WEBHOOK')  # Discord Webhook Url
# wh_username = getenv('D_WEBHOOK_USERNAME')
# wh_avatar = getenv('D_WEBHOOK_AVATAR')

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
