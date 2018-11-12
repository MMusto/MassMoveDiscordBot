import discord
from discord.ext import commands
import os
import youtube_dl
from discord import opus
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

TOKEN = os.environ["TOKEN"]
client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
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
async def mcc(ctx, chname1 : str, chname2 : str) -> None:
	'''"Move-Channel-to-Channel" : .mcc (CHANNEL 1) (CHANNEL 2) -  Moves everyone from Channel 1 to Channel 2'''
	if ctx.message.author.server_permissions.move_members:
		server = ctx.message.server
		ch1 = get_channel(server, chname1)
		ch2 = get_channel(server, chname2)
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
		await client.delete_message(ctx.message)
	else:
		await client.say("Sorry you don't have permissions for that.")
		
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
						await client.say("Moved Member: " + member.name + " with role " + got_role.name + " to channel " + ch.name)
		await client.delete_message(ctx.message)
	else:
		await client.say("Sorry you don't have permissions for that.")
					
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

@client.command(pass_context=True)			
async def join(ctx):
	channel = ctx.message.author.voice.voice_channel
	await client.join_voice_channel(channel)
	
@client.command(pass_context=True)			
async def leave(ctx):
	server = ctx.message.server
	voice_client = client.voice_client_in(server)
	await voice_client.disconnect()
	
@client.command(pass_context=True)	
async def play(ctx, url):
	channel = ctx.message.author.voice.voice_channel
	server= ctx.message.server
	if client.voice_client_in(server) == None:
		await client.join_voice_channel(channel)
	voice_client = client.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url)
	players[server.id] = player
	player.start()
	
@client.command(pass_context=True)	
async def pause(ctx):
	server = ctx.message.server
	player = players[server.id]
	player.pause()
			
client.run(TOKEN)
