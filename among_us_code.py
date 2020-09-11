import asyncio
import discord
from discord.ext import commands

CODE_CHANNEL_ID = 753825645032767559
class AmongUs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == CODE_CHANNEL_ID and self.bot.user != message.author:
            channel = message.channel
            code = message.content
            await channel.purge(limit=None)
            await channel.send(f"Among Us Room Code: **{code}**")