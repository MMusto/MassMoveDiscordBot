from client import client as client
from discord import opus
import youtube_dl

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