import asyncio
import discord
from discord.ext import commands
import datetime

CODE_CHANNEL_ID = 753825645032767559
class AmongUs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)

    def valid_code(self, code : str):
        return  code.isalpha() and len(code) == 4

    @commands.Cog.listener()
    async def on_message(self, message):
        #Taken from https://stackoverflow.com/questions/62503897/how-can-i-limit-the-on-message-replies-discord-python-bot/62504583#62504583
        channel = message.channel
        if channel.id == CODE_CHANNEL_ID:
            now = datetime.datetime.utcnow()
            time_difference = (now - self.last_timeStamp).total_seconds()
            code = message.content.strip()
            author = message.author
            if time_difference > 5  and self.bot.user != author and self.valid_code(code):
                    await channel.purge(limit=None)
                    await channel.send(f"Among Us Room Code: **{code.upper()}**")
                    print(f"[SUCCESS - {(now.hour - 8) % 24}:{now.minute}] Code '{code}' was set by {author.display_name} / {author.name}")
                    self.last_timeStamp = datetime.datetime.utcnow()
            else:
                print(f"[FAILED - {(now.hour - 8) % 24}:{now.minute}] Code TRIED to be set to '{code}' by {author.display_name} / {author.name}")
                await message.delete()
                
    @commands.command(hidden = True)
    async def testembed(self, ctx):
        embed = discord.Embed(title = f"**AMONG US**")
        embed.add_field(name = "ROOM CODE", value = "**TEST**", inline = False)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)