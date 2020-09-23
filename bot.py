from os import environ
import discord
from discord.ext import commands
import asyncio
from among_us_code import AmongUs
from shaker import Shaker
from join_msgs import JoinSound
from massmove import MassMove
# from snooper import Snooper

# Documentation used: https://discordpy.readthedocs.io/en/latest/api.html

# Token is stored in Heroku environment to avoid
# the vulnerability of private Discord bot key exposed to public
TOKEN = environ["TOKEN"]
client = commands.Bot(command_prefix = '.')
client.add_cog(AmongUs(client))
client.add_cog(Shaker(client))
client.add_cog(JoinSound(client))
client.add_cog(MassMove(client))
# Run bot
client.run(TOKEN)