import discord
from discord.ext import commands
import os
import youtube_dl
from discord import opus

TOKEN = os.environ["TOKEN"]
client = commands.Bot(command_prefix = '.')

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

@client.event
async def on_ready():
	client.loop.create_task(bg())
	print(client.user.name)
	print("**********THE BOT IS READY**********")
	
@client.command(pass_context=True)
async def mah(ctx) -> None:
	'''"Move-All-Here" : Moves everyone to your current voice channel '''
	author = ctx.message.author
	server = author.server
	all_members = server.members
	channels = server.channels
	if author.server_permissions.move_members:
		#Finds voice channel that author is in
		for channel in channels:
			if(str(channel.type) == 'voice' and  author in channel.voice_members):
					move_channel = channel
					break
		#Moves all people to your channel that was found above
		for member in all_members:
			if(member.voice_channel != None and not member.is_afk and member != author):
				await client.move_member(member, move_channel)
				await client.say("Mass moved everyone to " + str(move_channel))
		await client.delete_message(ctx.message)
	else:
		await client.say("Sorry you don't have permissions for that.")
		
def get_channel(server, chname : str) -> "Channel":
	'''Helper function that returns Channel object from name snippet'''
	for channel in server.channels:
			if(str(channel.type) == 'voice'):
					if(chname.lower() in channel.name.lower()):
							return channel
	return None
		
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
				await mbr_helper(server, role, ch2)
	else:
		await client.say("Sorry you don't have permissions for that.")
	await client.delete_message(ctx.message)
	
async def mbr_helper(server, role : str, ch):
	'''Based off mbr. Integrated for use in .mcc'''
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
					
def get_role(server, role : str) -> 'Role':
	'''Helper function that returns Role object from name snippet'''
	for roleo in server.roles:
		if role.lower() in roleo.name.lower():
			return roleo
	return None
	
# @client.command(pass_context=True)
# async def clear(ctx,lim=1) -> None:
	# '''*(WIP)* Clears all error messages from this bot'''
	# dlist = []
	# async for message in client.logs_from(ctx.message.channel,limit=int(lim)):
		# dlist.append(message)
	# await client.delete_messages(dlist)

@client.command()
async def ping():
	await client.say("Pong!")
		
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

# @client.command(pass_context=True)			
# async def join(ctx):
	# channel = ctx.message.author.voice.voice_channel
	# await client.join_voice_channel(channel)
	
# @client.command(pass_context=True)			
# async def leave(ctx):
	# server = ctx.message.server
	# voice_client = client.voice_client_in(server)
	# await voice_client.disconnect()
	
# @client.command(pass_context=True)	
# async def play(ctx, url):
	# channel = ctx.message.author.voice.voice_channel
	# server= ctx.message.server
	# if client.voice_client_in(server) == None:
		# await client.join_voice_channel(channel)
	# voice_client = client.voice_client_in(server)
	# player = await voice_client.create_ytdl_player(url)
	# players[server.id] = player
	# player.start()
	
# @client.command(pass_context=True)	
# async def pause(ctx):
	# server = ctx.message.server
	# player = players[server.id]
	# player.pause()
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

@client.command(pass_context=True)
async def lib(ctx, url):
	#url = 'sound\\' + url
	url = url.lower()
	if url != 'list':
		channel = ctx.message.author.voice.voice_channel
		server= ctx.message.server
		if client.voice_client_in(server) == None:
			await client.join_voice_channel(channel)
		voice_client = client.voice_client_in(server)
		player = voice_client.create_ffmpeg_player(filename = url+'.mp3')
		player.start()
	else:
		await client.say("MP3 Name List: bencry, benKO, noi, sfcl, money, pussyboi, zackstop, chillis, mskeisha, aknife, achild, kyle, wednesday, lebronjames, notmydad, eggsma, iloveubitch, slaverysorry, roadwork, delisioso, online, skate, cowboy, countryboy, oovoo, chickens, okay")
	
client.run(TOKEN)
