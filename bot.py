# bot.py
import os
import re
import discord
from discord import colour
from dotenv import load_dotenv

load_dotenv('./.env')
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('MY_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guild = discord.utils.get(client.guilds, name=GUILD)
    channel = guild.system_channel
    await channel.send('I\'m here!')

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    matches = re.findall('(?<=r\/)[0-9A-Za-z][0-9A-Za-z_]*(?= |$)', message.content)
    if matches:
        bot_message = ''
        for match in matches:
            bot_message += '[' + match + '](https://www.reddit.com/r/' + match + ')\n'
        await message.channel.send(embed=discord.Embed(title='Linked Subreddits', description=bot_message[:-1], color=colour.Color(0xFF4500)))

client.run(TOKEN)
