from discord.ext import commands
import discord
import time

BOT_TOKEN = "MTEwNjg4MTQ3Mzg4NzM1NDkyMA.GnJyMI.zDem2-TA8XVOtqKNOnNAeVMGQd_VDV7K78zBmw" #Discord Bot Token
CHANNEL_ID = 1043860127054319621 #Discord Text Channel

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
