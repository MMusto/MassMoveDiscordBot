from os import environ
import discord
from discord.ext import commands
import asyncio
from search import Search
from among_us_code import AmongUs
from shaker import Shaker
from join_msgs import JoinSound
# from snooper import Snooper

# Documentation used: https://discordpy.readthedocs.io/en/latest/api.html

# Token is stored in Heroku environment to avoid
# the vulnerability of private Discord bot key exposed to public
TOKEN = environ["TOKEN"]
client = commands.Bot(command_prefix = '.')

# TODO : Refactor into object cog
control_panel = None
message_to_channel = {}
mm_reaction_emoji_1 = '🔼'
mm_reaction_emoji_2 = '🔵'
mm_reaction_channel_name = 'mass-move-reactions'
server_name = 'execute'


@client.event
async def on_ready():
    print(f"[!] {client.user.name} initializing...")
    await start_mass_move_reactions()
    print(f"[!] {client.user.name} initialization complete!")

######################################## HELPER FUNCTIONS ############################################
######################################## HELPER FUNCTIONS ############################################    
def error(msg):
    print("Error: " + msg)
    
def get_channel(server, chname : str) -> "Channel":
    '''Helper function that returns Channel object from name snippet'''
    for channel in server.channels:
        if(str(channel.type) == 'voice'):
                if(chname.lower() in channel.name.lower()):
                        return channel
    return None
    
async def mbr_helper(server, role : str, ch1, ch2) -> "None":
    '''Based off mbr. Integrated for use in .mcc'''
    got_role = get_role(server, role)

    all_members = ch1.members
    for member in all_members:
        for rolee in member.roles:
            if rolee == got_role:
                await member.move_to(ch2)

def get_role(server, role_name : str) -> 'Role':
    '''Helper function that returns Role object from name snippet'''
    for role in server.roles:
        if role_name.lower() in role.name.lower():
            return role
    return None

def permission_to_move(user):
	return user.guild_permissions.move_members
                    
######################################## END OF HELPER FUNCTIONS ############################################
######################################## END OF HELPER FUNCTIONS ############################################

async def start_mass_move_reactions():
    '''Init mass move'''
    global control_panel

    exe = None
    async for server in client.fetch_guilds():
        if server_name in server.name.lower():
            exe = server
            break
    if not exe:
        error(f"{server_name} not found in function 'start_mass_move_reactions'")
        return

    voice_channels = {}
    channels = await exe.fetch_channels()
    for channel in channels:
        if type(channel) is discord.channel.VoiceChannel:
            voice_channels[channel.name] = channel
        elif type(channel) is discord.channel.TextChannel and mm_reaction_channel_name in channel.name:
            control_panel = channel

    if not control_panel:
        error("Control Channel not found in function 'start_mass_move_reactions'")
        return

    await control_panel.purge(limit=None)

    for channel in sorted(voice_channels.keys(), key = lambda channel_name: voice_channels[channel_name].position):
        name = "**"+channel+"**"
        message = await control_panel.send(embed = discord.Embed(title = name))
        await message.add_reaction(mm_reaction_emoji_1)
        await message.add_reaction(mm_reaction_emoji_2)
        message_to_channel[message.id] = voice_channels[channel].id

    await control_panel.send(f"**Click the {mm_reaction_emoji_1} emoji underneath the channel you wish to move everyone from. Then click the {mm_reaction_emoji_2} emoji underneath the channel you wish to move everyone to.**")
    
@client.command(pass_context=True)
async def rr(ctx):
    if(permission_to_move(ctx.author)):
        await start_mass_move_reactions()

@client.command(pass_context=True)
async def mg(ctx, game, chname):
    ''' "Move game": Moves everyone playing "game" to channel with chname in channel name '''
    author = ctx.author
    server = ctx.guild
    all_members = server.members
    if permission_to_move(author):
        move_channel = get_channel(server, chname)
        #Moves all people to specified channel if they have game in their currently playing game
        for member in all_members:
            if(member.voice != None and member.voice.channel and not member.voice.afk and game.lower() in str(member.game).lower()):
                await member.move_to(move_channel)
        await ctx.send(f"Mass moved everyone playing { game } to {str(move_channel)}")
    else:
        await ctx.send(f"Sorry you don't have permissions for that, {ctx.author.mention}")

@client.command(pass_context=True)
async def mah(ctx) -> None:
    ''' "Move-All-Here" : Moves everyone to your current voice channel '''
    author = ctx.author
    server = ctx.guild
    all_members = server.members
    if permission_to_move(author):
        if author.voice:
            move_channel = author.voice.channel
        else:
            await ctx.send(f"You have to be in a Voice Channel to use this command, {ctx.author.mention}")
            return
        #Moves all people to author's channel
        for member in all_members:
            if(member.voice and not member.voice.afk and member != author):
                await member.move_to(move_channel)
        await ctx.send(f"Mass moved everyone to {str(move_channel)}")
        await ctx.message.delete()
    else:
        await ctx.send(f"Sorry you don't have permissions for that, {ctx.author.mention}")
        
@client.command(pass_context=True)
async def mcc(ctx, src_name : str, dst_name : str, *roles) -> None:
    ''' "Move-Channel-to-Channel" : .mcc (SRC CHANNEL) (DEST CHANNEL) [roles to move] -  Moves everyone from SRC to DEST. If roles are included, only users with the specified roles will be moved '''
    if permission_to_move(ctx.author):
        server = ctx.message.guild
        src_channel = get_channel(server, src_name)
        dst_channel = get_channel(server, dst_name)
        
        if len(roles) == 0:
            if(src_channel is None and dst_channel is not None):
                await ctx.send(f"Sorry, '{src_name}' could not be found.")
            elif(dst_channel is None and src_channel is not None):
                await ctx.send(f"Sorry, '{dst_name}' could not be found.")
            elif(dst_channel is None and src_channel is None):
                await ctx.send(f"Sorry, both '{src_name}' and  '{dst_name}' could not be found.")
            else:
                lst = [member.move_to(dst_channel) for member in src_channel.members]
                await asyncio.gather(*lst)
        else:
            for role in roles:
                await mbr_helper(server, role, src_channel, dst_channel)
    else:
        await ctx.send(f"Sorry you don't have permissions for that, {ctx.author.mention}")
    
@client.command(pass_context=True)
async def mbr(ctx, role_name: str, chname: str) -> None:
    ''' "Move-By-Role" : .mbr (ROLE_NAME) (CHANNEL x) -  Moves everyone from with ROLE_NAME in one of their roles to CHANNEL x '''
    if permission_to_move(ctx.author):
        server = ctx.message.guild
        ch = get_channel(server, chname)
        got_role = get_role(server, role_name)
        all_members = server.members

        if(ch is None and got_role is None):
            await ctx.send(f"Sorry, both '{chname}' and '{role_name}' could not be found.")
        elif(ch is None):
            await ctx.send(f"Sorry, '{chname}' could not be found.")
        elif(got_role is None):
            await ctx.send(f"Sorry, '{role_name}' could not be found.")
        for member in all_members:
            if(member.voice is not None and member.voice.channel != ch and not member.voice.afk):
                for role in member.roles:
                    if role == got_role:
                        await member.move_to(ch)
                        # await ctx.send("Moved Member: " + member.name + " with role " + got_role.name + " to channel " + ch.name)
    else:
        await ctx.send(f"Sorry you don't have permissions for that, {ctx.author.mention}")
    await ctx.message.delete()   

@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        if(permission_to_move(user) and reaction.message.channel == control_panel and reaction.emoji == mm_reaction_emoji_1 and reaction.message.id in message_to_channel):
            src_channel = client.get_channel(message_to_channel[reaction.message.id])

            def check(r,u):
                return r.emoji == mm_reaction_emoji_2 and u == user and r.message.id in message_to_channel

            next_reaction, _ = await client.wait_for('reaction_add', check = check)
            dst_channel = client.get_channel(message_to_channel[next_reaction.message.id])

            members_to_move = [member.move_to(dst_channel) for member in src_channel.members]
            print(f"{user.display_name}/{user.name} moved everyone from {src_channel.name} to {dst_channel.name}")
            await reaction.message.remove_reaction(mm_reaction_emoji_1, user)
            await next_reaction.message.remove_reaction(mm_reaction_emoji_2, user)
            await asyncio.gather(*members_to_move)

client.add_cog(Search(client))
client.add_cog(AmongUs(client))
client.add_cog(Shaker(client))
client.add_cog(JoinSound(client))
# client.add_cog(Snooper(client))
# Run bot
client.run(TOKEN)