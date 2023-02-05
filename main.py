from discord.ext import commands
import discord
import logging
import config

logging.basicConfig(level=logging.INFO)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='.', help_command=None, intents=intents)


@bot.event
async def on_ready():
    print('Rigged for silent running')

bot.load_extension('awair')
print("awair initiated")

bot.run(config.bot_key)
