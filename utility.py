from client import client as client
from helper import permission_to_move
import discord

@client.command(pass_context=True)
async def clear(ctx, lim=1) -> None:
    '''*(WIP)* Clears all error messages from this bot'''
    if(ctx.message.author.server_permissions.manage_messages):
        deleted = await ctx.channel.purge(limit=lim)
        await client.send(f"Deleted {len(deleted)} messages", delete_after=2.0)


@client.command(pass_context=True)
async def setgame(ctx, gam):
    '''Modify game played by bot in friends list/status bar'''
    if permission_to_move(ctx.message.author):
        await client.change_presence(activity=discord.Game(name=gam))