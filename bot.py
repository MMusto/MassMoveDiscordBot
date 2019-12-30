from client import client as client
import os
import youtube_dl
import discord
from discord import opus
from helper import *
import musicplayer
import asyncio
import utility

#Documentation used: https://discordpy.readthedocs.io/en/async/api.html

#Token is stored in Heroku environment to avoid 
#the vulnerability of private Discord bot key exposed to public
TOKEN = os.environ["TOKEN"]

control_panel = None
voice_channels = {}
mm_reaction_emoji_1 = '🔼'
mm_reaction_emoji_2 = '🔵'
mm_reaction_channel_name = 'mass-move-reactions'
server_name = 'execute'
channel_sep = "**--------------------------------------**"

@client.event
async def on_ready():
    #client.loop.create_task(bg())
    
    await start_mass_move_reactions()
    print(client.user.name)
    print("**********THE BOT IS READY**********")

######################################## MASS_MOVE FUNCTIONS ############################################
######################################## MASS_MOVE FUNCTIONS ############################################

async def start_mass_move_reactions():
    '''Init mass move'''
    global control_panel
    global voice_channels
    
    exe = None
    for server in client.servers:
        if server_name in server.name.lower():
            exe = server
            break
    if not exe:
        error("Exe not found in function 'start_mass_move_reactions'")
        return
        
    for channel in exe.channels:
        if(str(channel.type) == 'voice'):
            voice_channels[channel.name] = channel
        else:
            if mm_reaction_channel_name in channel.name:
                control_panel = channel
    if not control_panel:
        error("Control Channel not found in function 'start_mass_move_reactions'")
        return
        
    await client.purge_from(channel = control_panel, limit=100)
    await client.send_message(control_panel, channel_sep)
    for channel in sorted(voice_channels.keys(), key = lambda x: voice_channels[x].position):
        name = "**"+channel+"**"
        message = await client.send_message(control_panel, embed = discord.Embed(title = name))
        await client.add_reaction(message, mm_reaction_emoji_1)
        await client.add_reaction(message, mm_reaction_emoji_2)
        #await client.send_message(control_panel, channel_sep)
    await client.send_message(control_panel, "**Click the " + mm_reaction_emoji_1 + " emoji underneath the channel you wish to move everyone from. Then click the " + mm_reaction_emoji_2 + " emoji underneath the channel you wish to move everyone to.**")
   
@client.command(pass_context=True)
async def rr(ctx):
    if(ctx.message.author.server_permissions.manage_messages):
        await start_mass_move_reactions()
    
@client.command(pass_context = True)
async def mg(ctx, game, chname):
    ''' "Move game": Moves everyone playing "game" to channel with chname in channel name '''
    author = ctx.message.author
    server = author.server
    all_members = server.members
    if author.server_permissions.move_members:
        move_channel = get_channel(server, chname)
        #Moves all people to specified channel if they have game in their currently playing game
        for member in all_members:
            print(member.game)
            if(member.voice_channel != None and not member.is_afk and game.lower() in str(member.game).lower()):
                await client.move_member(member, move_channel)
        await client.say("Mass moved everyone playing " + game + " to " + str(move_channel))
    else:
        await client.say("Sorry you don't have permissions for that.")
        
@client.command(pass_context=True)
async def mah(ctx) -> None:
    ''' "Move-All-Here" : Moves everyone to your current voice channel '''
    author = ctx.message.author
    server = author.server
    all_members = server.members
    channels = server.channels
    if author.server_permissions.move_members:
        move_channel = author.voice.voice_channel
        #Moves all people to author's channel
        for member in all_members:
            if(member.voice_channel != None and not member.is_afk and member != author):
                await client.move_member(member, move_channel)
                await client.say("Mass moved everyone to " + str(move_channel))
        await client.delete_message(ctx.message)
    else:
        await client.say("Sorry you don't have permissions for that.")
        
@client.command(pass_context=True)
async def mcc(ctx, chname1 : str, chname2 : str, *arg) -> None:
    ''' "Move-Channel-to-Channel" : .mcc (CHANNEL 1) (CHANNEL 2) [roles to move] -  Moves everyone from Channel 1 to Channel 2. If roles are included, only users with the specified roles will be moved '''
    if ctx.message.author.server_permissions.move_members:
        server = ctx.message.server
        ch1 = get_channel(server, chname1)
        ch2 = get_channel(server, chname2)
        if arg == ():
            if(ch1 == None and ch2 != None):
                await client.say("Sorry, '" + chname1 + "' could not be found.")
            elif(ch2 == None and ch1 != None):
                await client.say("Sorry, '" + chname2 + "' could not be found.")
            elif(ch2 == None and ch1 == None):
                await client.say("Sorry, both '" + chname1 + "' and  '" + chname2 + "' could not be found.")
            else:
                lst = [client.move_member(member, ch2) for member in ch1.voice_members]
                await asyncio.gather(*lst)
        else:
            for role in arg:
                await mbr_helper(server, role, ch1, ch2)
    else:
        await client.say("Sorry you don't have permissions for that.")
    #await client.delete_message(ctx.message)
    

                    
@client.command(pass_context=True)
async def mbr(ctx, role : str, chname : str) -> None:
    ''' "Move-By-Role" : .mbr (ROLE_NAME) (CHANNEL x) -  Moves everyone from with ROLE_NAME in one of their roles to CHANNEL x '''
    if ctx.message.author.server_permissions.move_members:
        server = ctx.message.server
        ch = get_channel(server, chname)
        got_role = get_role(server, role)
        all_members = server.members
                
        if(ch == None and got_role == None):
            await client.say("Sorry, both '" + chname + "' and '" + role + "' could not be found.")
        elif(ch == None):
            await client.say("Sorry, '" + chname + "' could not be found.")
        elif(got_role == None):
            await client.say("Sorry, '" + role + "' could not be found.")
        for member in all_members:
            if(member.voice_channel != None and member.voice_channel != ch and not member.is_afk):
                for rolee in member.roles:
                    if rolee == got_role:
                        await client.move_member(member, ch)
                        #await client.say("Moved Member: " + member.name + " with role " + got_role.name + " to channel " + ch.name)
    else:
        await client.say("Sorry you don't have permissions for that.")
    await client.delete_message(ctx.message)

######################################## END OF MASS_MOVE FUNCTIONS ############################################
######################################## END OF MASS_MOVE FUNCTIONS ############################################        

@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        if(user.server_permissions.manage_messages and reaction.message.channel == control_panel and reaction.emoji == mm_reaction_emoji_1):
            global voice_channels
            ch1 = voice_channels[reaction.message.content.strip('*')]
            next_reaction, user = await client.wait_for_reaction(emoji = mm_reaction_emoji_2, user=user) #if person uses emoji on an unintended message, function breaks
            ch2 = voice_channels[next_reaction.message.content.strip('*')]
            lst = {client.move_member(member, ch2) for member in ch1.voice_members}
            print("{}/{} moved everyone from {} to {}".format(user.display_name, user.name, ch1.name, ch2.name))
            await asyncio.gather(*lst)
            await client.remove_reaction(reaction.message, mm_reaction_emoji_1, user)
            await client.remove_reaction(next_reaction.message, mm_reaction_emoji_2, user)
            return
            
            
            
@client.command(pass_context=True)
async def lib(ctx, url):
    #url = 'src\\' + url
    url = url.lower()
    if url != 'list':
        channel = ctx.message.author.voice.voice_channel
        server = ctx.message.server
        if client.voice_client_in(server) == None:
            await client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
        player = voice_client.create_ffmpeg_player(filename = url+'.mp3')
        player.start()
    else:
        await client.say("MP3 Name List: bencry, benko, noi, sfcl, money, zackstop, chillis, mskeisha, aknife, achild, kyle, wednesday, lebronjames, notmydad, eggsma, roadwork, delicioso, online, skate, cowboy, countryboy, oovoo, chickens, okay")

#Run bot
        
client.run(TOKEN)