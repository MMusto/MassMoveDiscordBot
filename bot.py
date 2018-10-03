import discord
from discord.ext import commands
import discord.utils
import time
import os

TOKEN = os.environ["TOKEN"]

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
	print("bot is ready")
	
@client.command(pass_context=True)
async def mah(ctx):
	'''"Move-All-Here" : Moves everyone to your current voice channel '''
	author = ctx.message.author
	if author.server_permissions.move_members:
		for channel in client.get_all_channels():
			if(str(channel.type) == 'voice' and  author in channel.voice_members):
					move_channel = channel
					break
		for member in client.get_all_members():
			if(member.voice_channel != None and not member.is_afk and member != author):
				await client.move_member(member, move_channel)
				await client.say("Moved " + str(member) + " to " + str(move_channel))
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
async def mcc(ctx, chname1 : str, chname2 : str):
	'''"Move-Channel-to-Channel" : .mcc (CHANNEL 1) (CHANNEL 2) -  Moves everyone from Channel 1 to Channel 2'''
	ch1 = get_channel(chname1)
	ch2 = get_channel(chname2)
	if ch1 == None and ch2 != None:
		await client.say("Sorry, '" + chname1 + "' could not be found.")
	elif ch2 == None and ch1 != None:
		await client.say("Sorry, '" + chname2 + "' could not be found.")
	elif ch2 == None and ch1 = None:
		await client.say("Sorry, both '" + chname1 + "' and  '" + chname2 + "' could not be found.")
	else:
		lst = []
		for member in get_channel(chname1).voice_members:
			lst.append(member)
		for member in lst:
			await client.move_member(member, ch2)
@client.command
async def commands():
	await client.say('.mah - "Move-All-Here : Moves all players to your current voice channel')
	await client.say('.mcc - "Move-Channel-To-Channel" : .mcc (CHANNEL 1) (CHANNEL 2)  Moves all players from first channel to second channel')


client.run(TOKEN)