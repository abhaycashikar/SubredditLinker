# bot.py
import os
import re
import discord
from discord.errors import NotFound
import praw
from discord import colour
from dotenv import load_dotenv
import prawcore

load_dotenv('./.env')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('MY_GUILD')
ORANGE = colour.Color(0xFF4500)
PFP = 'https://github.com/abhaycashikar/SubredditLinker/raw/main/pfp.png'
# STATUS_TEXT = 'Tag me for help!'
FOOTER = 'Found an issue? Tag the bot to get the GitHub link!'
FOOTER_ICON = 'https://github.com/abhaycashikar/SubredditLinker/raw/main/question_mark.png'

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
    # emojis = list(filter(lambda e: e.name == 'question', client.emojis))
    # activity = discord.CustomActivity(STATUS_TEXT, emoji=emojis[0] if emojis else None)
    # await client.change_presence(activity=activity)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for a mention!"))
    await channel.send('I\'m here!')

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    if client.user in message.mentions:
        embed = discord.Embed(
            title='SubredditLinker',
            url='https://github.com/abhaycashikar/SubredditLinker',
            description='Links to and displays basic info for subreddit names (i.e. "r/" followed by a string) in user messages.',
            color=ORANGE
        )
        embed.set_thumbnail(url=PFP)
        embed.add_field(name='Found an issue?', value='[Let me know!](https://github.com/abhaycashikar/SubredditLinker/issues)')
        await message.channel.send(embed=embed)

    matches = re.findall('(?<!\/)r\/[0-9A-Za-z][0-9A-Za-z_]*(?= |$)', message.content)
    if matches:
        maxed_matches = False
        if len(matches) > 5:
            matches = matches[:5]
            maxed_matches = True

        for match in matches:
            try:
                subreddit = reddit.subreddit(match[2:])
                desc: str = subreddit.public_description
                if desc.find('\n') in range(200):
                    desc = desc[:desc.find('\n')]
                elif len(desc) > 203:
                    desc = desc[:200] + '...'
                embed = discord.Embed(
                    title=match,
                    url='https://reddit.com/' + match,
                    description=desc,
                    color=ORANGE)
                embed.set_thumbnail(url=subreddit.icon_img if subreddit.icon_img else subreddit.community_icon)
                embed.set_footer(text=FOOTER, icon_url=FOOTER_ICON)
                post_links = []
                for post in subreddit.top(limit=3):
                    post_links.append('[' + post.title + '](' + post.url + ')')
                embed.add_field(name='Top Posts of All Time', value='\n'.join(post_links))
                await message.channel.send(embed=embed)
            except prawcore.exceptions.Forbidden:
                embed = discord.Embed(
                    title=match,
                    url='https://reddit.com/' + match, 
                    description='Could not fetch details because ' + match + ' is either a private or quarantined subreddit.',
                    color=ORANGE
                )
                embed.set_footer(text=FOOTER, icon_url=FOOTER_ICON)
                await message.channel.send(embed=embed)
            except prawcore.exceptions.NotFound:
                embed = discord.Embed(
                    title=match,
                    description=match + ' is either a banned subreddit, or it does not exist.',
                    color=ORANGE
                )
                embed.set_footer(text=FOOTER, icon_url=FOOTER_ICON)
                await message.channel.send(embed=embed)

        if maxed_matches:
            await message.channel.send(content='Can only link five subreddits at a time.')

client.run(DISCORD_TOKEN)