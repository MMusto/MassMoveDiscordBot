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
    
    def log(self, msg : str) -> None:
        """Logs to Heroku log console.

        Args:
            msg (str): log message
        """
        now = datetime.datetime.utcnow()
        current_time_str = f"{(now.hour - 7) % 24}:{now.minute}"
        print(f"[{current_time_str}] {msg}")

    def valid_code(self, code : str) -> bool:
        """Returns whether the given Among Us code string is valid

        Args:
            code (str): code string

        Returns:
            bool: True is valid code string
        """
        return code.isalpha() and len(code) == 6

    def get_embed(self, code : str) -> discord.Embed:
        """Returns a nicely formatted embed object that we can send in a discord message.

        Args:
            code (str): formatted code string

        Returns:
            discord.Embed: Nicely formatted embed object with Among Us code
        """
        embed = discord.Embed(title = "Room Code:", color = 0x00f715)
        embed.add_field(name = f"**{code}**", value = "**   **", inline = False)
        return embed

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message) -> None:
        """When a message containing a valid code is sent
           in the designated 'Among Us code channel' the 
           text channel is cleared and only the nicely 
           formatted valid code remains in the text channel

        Args:
            message (discord.Message): discord message (default argument for event listener)
        """
        channel = message.channel
        author = message.author

        if channel.id == CODE_CHANNEL_ID and self.bot.user != author:

            now = datetime.datetime.utcnow()
            time_difference = (now - self.last_timeStamp).total_seconds()
            code = message.content.strip()

            if time_difference > COOLDOWN and self.valid_code(code):
                    self.last_timeStamp = now
                    await channel.purge(limit=None)
                    await channel.send(embed = self.get_embed(code.upper()))
                    self.log(f"'{code}' was SUCCESSFULLY set by {author.display_name} / {author.name}")
            else:
                await message.delete()
                self.log(f"'{code}' FAILED to be set by {author.display_name} / {author.name}")
