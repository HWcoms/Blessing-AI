from discord.ext import commands
import discord
import time

from os import getenv
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = getenv('D_BOT_TOKEN') #Discord Bot Token
CHANNEL_ID = int(getenv('D_CHANNEL_ID')) #Discord Text Channel

bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

@bot.event
async def on_ready():
     print("hello bot is ready")
     channel = bot.get_channel(CHANNEL_ID)
     await channel.send("Silent message test", silent = True)
     
async def print_text(str):
     print("bot says: " + str)
     channel = bot.get_channel(CHANNEL_ID)
     # await channel.send("Silent message test", silent = True)

async def on_message(message):
     print(f"{message.author}: {message}")

bot.run(BOT_TOKEN)
