# bot.py
import os
import re
import discord
from discord.errors import NotFound
import praw
from discord import colour
from dotenv import load_dotenv

load_dotenv('./.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('MY_GUILD')

client = discord.Client()
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_ID'),
    client_secret=os.getenv('REDDIT_SECRET'),
    user_agent="discord:subredditlinker:v1.0.0 (by u/approvedcargo91)"
)

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
    matches = re.findall('(?<!\/)r\/[0-9A-Za-z][0-9A-Za-z_]*(?= |$)', message.content)
    if matches:
        bot_message = ''
        for match in matches:
            name = match[2:]
            try:
                subreddit = reddit.subreddit(name)
                desc: str = subreddit.public_description
                if desc.find('\n') in range(200):
                    desc = desc[:desc.find('\n')]
                elif len(desc) > 203:
                    desc = desc[:200] + '...'
                bot_message += '\n[' + name + '](https://www.reddit.com/r/' + name + ')\n' + desc + '\n'
            except:
                bot_message += '\n' + name + ' does not exist. Or maybe it\'s private?'
        await message.channel.send(embed=discord.Embed(title='Linked Subreddits', description=bot_message[1:-1], color=colour.Color(0xFF4500)))

client.run(DISCORD_TOKEN)
