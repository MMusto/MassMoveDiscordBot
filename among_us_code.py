import asyncio
import discord
from discord.ext import commands

CODE_CHANNEL_ID = 753818860100255884
class AmongUs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == CODE_CHANNEL_ID:
            channel = message.channel
            code = message.content
            await channel.purge(limit=None)
            await channel.send(f"Among Us Room Code: **{code}**")