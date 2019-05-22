import discord
from discord.ext import commands
import os
import youtube_dl
from discord import opus

TOKEN = os.environ["TOKEN"]
client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    client.loop.create_task(bg())
    print(client.user.name)
    print("**********THE BOT IS READY**********")

######################################## MASS_MOVE FUNCTIONS ############################################
######################################## MASS_MOVE FUNCTIONS ############################################    
@client.command(pass_context = True)
async def mg(ctx, game, chname):
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
    '''"Move-All-Here" : Moves everyone to your current voice channel '''
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
    '''"Move-Channel-to-Channel" : .mcc (CHANNEL 1) (CHANNEL 2) -  Moves everyone from Channel 1 to Channel 2'''
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
                lst = [member for member in ch1.voice_members]
                for member in lst:
                    await client.move_member(member, ch2)
        else:
            for role in arg:
                await mbr_helper(server, role, ch1, ch2)
    else:
        await client.say("Sorry you don't have permissions for that.")
    #await client.delete_message(ctx.message)
    

                    
@client.command(pass_context=True)
async def mbr(ctx, role : str, chname : str) -> None:
    '''"Move-By-Role" : .mbr (ROLE_NAME) (CHANNEL x) -  Moves everyone from with Role ROLE_NAME to Channel x'''
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

    
@client.command(pass_context=True)
async def clear(ctx,lim=1) -> None:
    '''*(WIP)* Clears all error messages from this bot'''
    if(user.server_permissions.manage_messages):
        dlist = []
        async for message in client.logs_from(ctx.message.channel,limit=int(lim)):
            dlist.append(message)
        await client.delete_messages(dlist)

@client.command(pass_context = True)
async def setgame(ctx, gam):
    if ctx.message.author.server_permissions.move_members:
        await client.change_presence(game=discord.Game(name=gam))
        
@client.event
async def on_reaction_add(reaction, user):
    if(user.server_permissions.manage_messages):
        channel = reaction.message.channel
        msg1 = reaction.message
        if(reaction.emoji == '🆑'):
            #await client.send_message(channel, user.name + " Set Marker at message '" + msg1.content + "' Please select second marker using " + '🔴')
            res = await client.wait_for_reaction(emoji = '🔴')
            msg2 = res.reaction.message
            count = 1
            if(msg1.timestamp < msg2.timestamp):
                first = msg2
                second = msg1
            else:
                first = msg1
                second = msg2
            dlist = [first]
            async for message in client.logs_from(channel, before=first):#after vs bfore switch
                #await client.delete_message(message)
                dlist.append(message)
                #print("Delete # " + str(count) + ": " + message.content)
                if(message.timestamp == second.timestamp):
                    #print("AT MSG 2: " + message.content)
                    break
                count += 1
            #await client.delete_message(first)
            await client.delete_messages(dlist)


@client.command(pass_context=True)
async def lib(ctx, url):
    #url = 'sound\\' + url
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
        await client.say("MP3 Name List: bencry, benko, noi, sfcl, money, pussyboi, zackstop, chillis, mskeisha, aknife, achild, kyle, wednesday, lebronjames, notmydad, eggsma, iloveubitch, slaverysorry, roadwork, delicioso, online, skate, cowboy, countryboy, oovoo, chickens, okay, lfdh, gayppl, mong0, mong1, mong2, mong3, mong4, mongfull, coming, looseass, note, suh")
    
@client.command(pass_context = True)
async def gas(ctx, *arg):
    if ctx.message.author.server_permissions.move_members:
        server = ctx.message.server
        all_members = server.members
        channel = get_channel(server, "gas")
        voice = await client.join_voice_channel(channel)
        player = voice.create_ffmpeg_player(filename = 'gas.mp3')
        members = set()
        if (arg[0] == 'ALL'):
            for member1 in all_members:
                if(member1.voice_channel != None and not member1.is_afk):
                    await client.move_member(member1, channel)
        else:
            names = [name.lower() for name in arg]
            for member in all_members:
                if names != []:
                    if member.voice != None:
                        for name in names:
                            remove = False
                            if name in member.name.lower():
                                members.add(member)
                                remove = True
                            if member.nick != None and name in member.nick.lower():
                                members.add(member)
                                remove = True
                            if remove:
                                names.remove(name)
                else:
                    break
            for member in members:
                await client.move_member(member, channel)
        player.start()

        
######################################## HELPER FUNCTIONS ############################################
######################################## HELPER FUNCTIONS ############################################    

def get_channel(server, chname : str) -> "Channel":
    '''Helper function that returns Channel object from name snippet'''
    for channel in server.channels:
            if(str(channel.type) == 'voice'):
                    if(chname.lower() in channel.name.lower()):
                            return channel
    return None
    
async def mbr_helper(server, role : str, ch1, ch2):
    '''Based off mbr. Integrated for use in .mcc'''
    got_role = get_role(server, role)
            
    if(ch1 == None and ch2 == None and got_role == None):
        await client.say("Sorry, channels or roles could not be found.")
    elif(ch1 == None):
        await client.say("Sorry, '" + ch1.name + "' could not be found.")
    elif(ch2 == None):
        await client.say("Sorry, '" + ch2.name + "' could not be found.")
    elif(got_role == None):
        await client.say("Sorry, '" + role + "' could not be found.")

    all_members = ch1.voice_members
    for member in all_members:
        for rolee in member.roles:
            if rolee == got_role:
                await client.move_member(member, ch2)

def get_role(server, role : str) -> 'Role':
    '''Helper function that returns Role object from name snippet'''
    for roleo in server.roles:
        if role.lower() in roleo.name.lower():
            return roleo
    return None
                    
######################################## END OF HELPER FUNCTIONS ############################################
######################################## END OF HELPER FUNCTIONS ############################################


########################################  Music Player Functions   ############################################
########################################  Music Player Functions   ############################################
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

    raise RuntimeError('Could not load an opus lib. Tried %s' %
                       (', '.join(opus_libs)))
opts = {
    'default_search': 'auto',
    'quiet': True,
}  # youtube_dl options

load_opus_lib()
players = {}
servers_songs={}
player_status={}
now_playing={}
song_names={}
paused={}

async def set_player_status():
    for i in client.servers:
        player_status[i.id]=False
        servers_songs[i.id]=None
        paused[i.id]=False
        song_names[i.id]=[]
    print(200)

async def check_voice(con):
    pass

async def bg():
    client.loop.create_task(set_player_status())
    
async def queue_songs(con,clear):
    if clear == True:
        song_names[con.message.server.id].clear()
        await client.voice_client_in(con.message.server).disconnect()
        player_status[con.message.server.id] = False

    if clear == False:

        if len(song_names[con.message.server.id])==0:
            servers_songs[con.message.server.id]=None

        if len(song_names[con.message.server.id]) !=0:
            song=await client.voice_client_in(con.message.server).create_ytdl_player(song_names[con.message.server.id][0], ytdl_options=opts, after=lambda: client.loop.create_task(after_song(con, False)))
            servers_songs[con.message.server.id]=song
            servers_songs[con.message.server.id].start()
            await client.delete_message(now_playing[con.message.server.id])
            msg=await client.send_message(con.message.channel,"Now playing {}".format(servers_songs[con.message.server.id].title))
            now_playing[con.message.server.id]=msg

            if len(song_names[con.message.server.id]) >= 1:
                song_names[con.message.server.id].pop(0)


        if len(song_names[con.message.server.id]) ==0 and servers_songs[con.message.server.id] == None:
            player_status[con.message.server.id]=False
        
async def after_song(con,clear):
    client.loop.create_task(queue_songs(con,clear))
    client.loop.create_task(check_voice(con))

@client.command(pass_context=True)
async def play(con,*,url):
    """PLAY THE GIVEN SONG AND QUEUE IT IF THERE IS CURRENTLY SOGN PLAYING"""
    check = str(con.message.channel)
    if check == 'Direct Message with {}'.format(con.message.author.name):
        await client.send_message(con.message.channel, "**You must be in a `server voice channel` to use this command**")

    if check != 'Direct Message with {}'.format(con.message.author.name):
        if client.is_voice_connected(con.message.server) == False:
            await client.join_voice_channel(con.message.author.voice.voice_channel)

        if client.is_voice_connected(con.message.server) == True:
            if player_status[con.message.server.id]==True:
                song_names[con.message.server.id].append(url)
                await client.send_message(con.message.channel, "**Song  Queued**")


                
            if player_status[con.message.server.id]==False:
                player_status[con.message.server.id]=True
                song_names[con.message.server.id].append(url)
                song=await client.voice_client_in(con.message.server).create_ytdl_player(song_names[con.message.server.id][0], ytdl_options=opts, after=lambda: client.loop.create_task(after_song(con,False)))
                servers_songs[con.message.server.id]=song
                servers_songs[con.message.server.id].start()
                msg = await client.send_message(con.message.channel, "Now playing {}".format(servers_songs[con.message.server.id].title))
                now_playing[con.message.server.id]=msg
                song_names[con.message.server.id].pop(0)




@client.command(pass_context=True)
async def skip(con):
    check = str(con.message.channel)
    if check == 'Direct Message with {}'.format(con.message.author.name):#COMMAND IS IN DM
        await client.send_message(con.message.channel, "**You must be in a `server voice channel` to use this command**")

    if check != 'Direct Message with {}'.format(con.message.author.name):#COMMAND NOT IN DM
        if servers_songs[con.message.server.id]== None or len(song_names[con.message.server.id])==0 or player_status[con.message.server.id]==False:
            await client.send_message(con.message.channel,"**No songs in queue to skip**")
        if servers_songs[con.message.server.id] !=None:
            servers_songs[con.message.server.id].pause()
            client.loop.create_task(queue_songs(con,False))



@client.command(pass_context=True)
async def join(con,channel=None):
    """JOIN A VOICE CHANNEL THAT THE USR IS IN OR MOVE TO A VOICE CHANNEL IF THE BOT IS ALREADY IN A VOICE CHANNEL"""
    check = str(con.message.channel)

    if check == 'Direct Message with {}'.format(con.message.author.name):#COMMAND IS IN DM
        await client.send_message(con.message.channel, "**You must be in a `server voice channel` to use this command**")

    if check != 'Direct Message with {}'.format(con.message.author.name):#COMMAND NOT IN DM
        voice_status = client.is_voice_connected(con.message.server)

        if voice_status == False:#VOICE NOT CONNECTED
            await client.join_voice_channel(con.message.author.voice.voice_channel)

        if voice_status == True:#VOICE ALREADY CONNECTED
            await client.send_message(con.message.channel, "**Bot is already connected to a voice channel**")



@client.command(pass_context=True)
async def leave(con):
    """LEAVE THE VOICE CHANNEL AND STOP ALL SONGS AND CLEAR QUEUE"""
    check=str(con.message.channel)
    if check == 'Direct Message with {}'.format(con.message.author.name):#COMMAND USED IN DM
        await client.send_message(con.message.channel,"**You must be in a `server voice channel` to use this command**")

    if check != 'Direct Message with {}'.format(con.message.author.name):#COMMAND NOT IN DM
        
        # IF VOICE IS NOT CONNECTED
        if client.is_voice_connected(con.message.server) == False:
            await client.send_message(con.message.channel,"**Bot is not connected to a voice channel**")

        # VOICE ALREADY CONNECTED
        if client.is_voice_connected(con.message.server) == True:
            client.loop.create_task(queue_songs(con,True))

@client.command(pass_context=True)
async def pause(con):
    check = str(con.message.channel)
    if check == 'Direct Message with {}'.format(con.message.author.name):# COMMAND IS IN DM
        await client.send_message(con.message.channel, "**You must be in a `server voice channel` to use this command**")

    # COMMAND NOT IN DM
    if check != 'Direct Message with {}'.format(con.message.author.name):
        if servers_songs[con.message.server.id]!=None:
            if paused[con.message.server.id] == True:
                await client.send_message(con.message.channel,"**Audio already paused**")
            if paused[con.message.server.id]==False:
                servers_songs[con.message.server.id].pause()
                paused[con.message.server.id]=True

@client.command(pass_context=True)
async def resume(con):
    check = str(con.message.channel)
    # COMMAND IS IN DM
    if check == 'Direct Message with {}'.format(con.message.author.name):
        await client.send_message(con.message.channel, "**You must be in a `server voice channel` to use this command**")

    # COMMAND NOT IN DM
    if check != 'Direct Message with {}'.format(con.message.author.name):
        if servers_songs[con.message.server.id] != None:
            if paused[con.message.server.id] == False:
                await client.send_message(con.message.channel,"**Audio already playing**")
            if paused[con.message.server.id] ==True:
                servers_songs[con.message.server.id].resume()
                paused[con.message.server.id]=False
                

######################################## End of Music Player Functions   ############################################
######################################## End of Music Player Functions   ############################################

        
client.run(TOKEN)
