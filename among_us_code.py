import asyncio
import discord
from discord.ext import commands
import datetime

COOLDOWN = 5
CODE_CHANNEL_ID = 753825645032767559

class AmongUs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)

    def valid_code(self, code : str):
        """Returns whether the given Among Us code is valid
           No preprocessing of the code string is done here. Ex. strip(), lower(), etc.

        Args:
            code (str): code string

        Returns:
            bool: True is valid code string
        """
        return code.isalpha() and len(code) == 6

    def get_embed(self, code : str) -> discord.Embed:
        """Returns an embed object with the code string (already formatted) that we can send in a discord message.

        Args:
            code (str): formatted code string

        Returns:
            discord.Embed: Nicely formatted embed object
        """
        embed = discord.Embed(title = "Room Code:", color = 0x00f715)
        embed.add_field(name = "**{code}**", value = "**   **", inline = False)
        return embed

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message) -> None:
        """When a message containing a valid code is sent
           in the designated 'Among Us code channel' the 
           text channel is cleared and only the nicely 
           formatted valid code remains in the text channel

        Args:
            message (discord.Message): discord
        """
        channel = message.channel

        if channel.id == CODE_CHANNEL_ID:

            now = datetime.datetime.utcnow()
            time_difference = (now - self.last_timeStamp).total_seconds()
            code = message.content.strip()
            author = message.author

            if time_difference > COOLDOWN  and self.bot.user != author and self.valid_code(code):
                    await channel.purge(limit=None)
                    await channel.send(embed = self.get_embed(code.upper()))
                    print(f"[SUCCESS - {(now.hour - 8) % 24}:{now.minute}] Code '{code}' was set by {author.display_name} / {author.name}")
                    self.last_timeStamp = datetime.datetime.utcnow()
            else:
                print(f"[FAILED - {(now.hour - 8) % 24}:{now.minute}] Code TRIED to be set to '{code}' by {author.display_name} / {author.name}")
                await message.delete()