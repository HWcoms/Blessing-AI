import requests

from os import getenv
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = getenv('D_BOT_TOKEN')            #Discord Bot Token
CHANNEL_ID = int(getenv('D_CHANNEL_ID'))     #Discord Text Channel

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