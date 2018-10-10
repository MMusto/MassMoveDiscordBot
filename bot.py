import discord
from discord.ext import commands
import os

TOKEN = os.environ["TOKEN"]

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
	print("**********THE BOT IS READY**********")
	
@client.command(pass_context=True)
async def mah(ctx) -> None:
	'''"Move-All-Here" : Moves everyone to your current voice channel '''
	author = ctx.message.author
	if author.server_permissions.move_members:
		#Finds voice channel that author is in
		for channel in client.get_all_channels():
			if(str(channel.type) == 'voice' and  author in channel.voice_members):
					move_channel = channel
					break
		#Moves all people to your channel that was found above
		for member in client.get_all_members():
			if(member.voice_channel != None and not member.is_afk and member != author):
				await client.move_member(member, move_channel)
				await client.say("Mass moved everyone to " + str(move_channel))
		client.delete_message(ctx.message)
	else:
		await client.say("Sorry you don't have permissions for that.")
		
def get_channel(chname : str) -> "Channel":
	'''Helper function that returns Channel object from name snippet'''
	for channel in client.get_all_channels():
			if(str(channel.type) == 'voice'):
					if(chname.lower() in channel.name.lower()):
							return channel
	return None
		
@client.command(pass_context=True)
async def mcc(ctx, chname1 : str, chname2 : str) -> None:
	'''"Move-Channel-to-Channel" : .mcc (CHANNEL 1) (CHANNEL 2) -  Moves everyone from Channel 1 to Channel 2'''
	ch1 = get_channel(chname1)
	ch2 = get_channel(chname2)
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
		client.delete_message(ctx.message)
		
@client.command(pass_context=True)
asycn def clear(ctx) -> None:
	'''Clears all error messages from this bot'''
	pass
	

client.run(TOKEN)
