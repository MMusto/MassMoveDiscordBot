import asyncio
import discord
from discord.ext import commands

CODE_CHANNEL_ID = 753825645032767559
class AmongUs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == CODE_CHANNEL_ID and self.bot.user != message.author and len(message.content) == 4:
            channel = message.channel
            code = message.content
            author = message.author
            await channel.purge(limit=None)
            await channel.send(f"Among Us Room Code: **{code}**")
            await channel.edit(name = f"among-us-code-{code}", topic = f"Code was set by {author.display_name} / {author.name}")