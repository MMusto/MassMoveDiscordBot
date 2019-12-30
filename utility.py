from client import client as client
import asyncio

@client.command(pass_context=True)
async def clear(ctx,lim=1) -> None:
    '''*(WIP)* Clears all error messages from this bot'''
    if(ctx.message.author.server_permissions.manage_messages):
        deleted = await client.purge_from(channel = ctx.message.channel, limit=lim+1)
        notification = await client.send_message(ctx.message.channel, "Deleted {} messages".format(len(deleted)))
        await asyncio.sleep(2)
        await client.delete_message(notification)
        # await client.delete_message(ctx.message)
        # async for message in client.logs_from(ctx.message.channel,limit=int(lim)):
            # await client.delete_message(message)
            
@client.command(pass_context = True)
async def setgame(ctx, gam):
    '''Modify game played by bot in friends list/status bar'''
    if ctx.message.author.server_permissions.move_members:
        await client.change_presence(game=discord.Game(name=gam))