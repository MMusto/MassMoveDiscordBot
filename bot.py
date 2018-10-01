import discord
from discord.ext import commands
import discord.utils
import time

TOKEN = 'NDk2MDM5MTg4ODE5NjA3NTYy.DpK05Q.hFReS4q5d0kLHOCh5yCQUbHFbGc'

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
	print("bot is ready")
	
@client.command(pass_context=True)
async def mah(ctx):
	'''"Move-All-Here" : Moves all players to your current voice channel '''
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
		
#Helper function for mcc
def get_channel(chname : str) -> "Channel":
	for channel in client.get_all_channels():
		if(str(channel.type) == 'voice'):
			if(chname.lower() in channel.name.lower()):
				return channel
	return None
		
@client.command(pass_context=True)
async def mcc(ctx, chname1 : str, chname2 : str):
	'''"Move-Channel-to-Channel" : .mcc (CHANNEL 1) (CHANNEL 2) -  Moves all players from first Channel 1 to Channel 2'''
	ch1 = get_channel(chname1).voice_members
	ch2 = get_channel(chname2)
	if ch1 == None or ch2 == None:
		await client.say("Sorry, one of the channels could not be found.")
	else:
		lst = []
		for member in get_channel(chname1).voice_members:
			lst.append(member)
		for member in lst:
			await client.move_member(member, ch2)
@client.command
async def help():
	await client.say('.mah - "Move-All-Here : Moves all players to your current voice channel')
	await client.say('.mcc - "Move-Channel-To-Channel" : .mcc (CHANNEL 1) (CHANNEL 2)  Moves all players from first channel to second channel')

client.run(TOKEN)