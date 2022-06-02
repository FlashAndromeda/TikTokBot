import logging
import os
import validators
import discord

import nest_asyncio
from TikTokApi import TikTokApi
from discord.ext import commands
from dotenv import load_dotenv

nest_asyncio.apply()

bot = commands.Bot(command_prefix='-tt', strip_after_prefix=True)
api = TikTokApi(logging_level=logging.INFO)

load_dotenv()
TOKEN = os.getenv('TOKEN')

class Debugging(commands.Cog, command_attrs=dict(hidden=True)):
    """
        A bunch of utility functions for debugging the bot.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = await bot.fetch_guilds(limit=100).flatten()
        print(f"{bot.user.name} has connected to discord!\n"
              f"I'm in {len(guilds)} guilds!\n")

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f"Latency is: `{round(bot.latency * 1000)}ms`")

class Tiktok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='video', aliases=['vid', 'v', 'download', 'down', 'd'], brief='Downloads a video by link.', usage='<link_to_video>')
    async def video(self, ctx, link:str):

        linkeval = validators.url(link)

        if linkeval:
            vid_id = os.path.split(str(link))[-1]
        else:
            vid_id = link

        video = api.video(id=vid_id).bytes()

        with open('video.mp4', 'wb') as out:
            out.write(video)

        size = os.path.getsize('video.mp4')
        limit = ctx.guild.filesize_limit

        if size >= limit:
            await ctx.send('Sorry, video too big to send in this server!\n'
                           f'File size is {round(size/1000000, 2)}MB while the upload limit is {round(limit/1000000, 2)}MB')
        else:
            await ctx.send(file=discord.File('video.mp4'))

        os.remove('video.mp4')

def setup(bot):
    bot.add_cog(Debugging(bot))
    bot.add_cog(Tiktok(bot))

setup(bot)
bot.run(TOKEN)
# https://discord.com/api/oauth2/authorize?client_id=981701817417228360&permissions=8&scope=bot%20applications.commands