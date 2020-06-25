# Mass Move Discord Bot
A Python based Discord bot that has a plethora of features including the ability to mass move users from channel to channel with simple, fast, and easy commands or reactions.

This bot can be run from your own computer or a dedicated host such as Heroku (This is how I run the bot 24/7 for free). 

Requirements are as follows:
1. Discord.py API wrapper found here: [Link](https://github.com/Rapptz/discord.py)
2. [Python 3.6.1](https://www.python.org/downloads/release/python-361/)
3. A Discord app. (You can create one [here](https://discordapp.com/developers/applications/))

## Setup
The **bot.py** is where the main app is run from. At the top of this file there are a few lines of config. The most important variables you need to modify are **TOKEN, mm_reaction_channel_name, and server_name**. 

Replace TOKEN with your own Discord bot's token. 

`TOKEN = 'YOUR_TOKEN_HERE'`

mm_reaction_channel_name is the name of the channel you wish to use for reaction-based mass-move. (You may just use a unique substring of the channel name. So 'test' would match the channel named 'hello-test-reaction-channel' because test is in the name and no other channel has 'test' in the name.) 

`mm_reaction_channel_name = 'CHANNEL_NAME_FOR_REACTION_MOVE'`

Finally, server_name is a substring or the full name of your server. (Not case-sensitive)

`server_name = 'MY_SERVER_NAME'`

## Some Commands
The default command prefix is '.' which can be changed in the **client.py** module.
* "Move-Channel-to-Channel" : 
  * .mcc (CHANNEL 1) (CHANNEL 2) [roles to move] -  Moves everyone from Channel 1 to Channel 2. If roles are included, only users with the specified roles will be moved
  
* "Clear" :
  * .clear x - Will clear the last x messages in the channel's history.-
 
* "Set Game" :
  * .setgame game - Modify game played by bot in friends list/status bar to be "game"
  
* **And much more**

The bot will automatically delete all messages in the reaction channel and include instructions on how to use the reaction mass move feature:
![image of mass move reaction chat](https://i.imgur.com/HzqgyOG.png)


You can change the emojis used by modifying the config variables at the top of the **bot.py** module. Also if you make any local changes that the running bot needs to know about (such as adding or moving around channels), simply use the ".rr" command and the corresponding changes will be updated. If you have any changes, bug fixes, or new feature ideas, simply reach out! Or if you would like to implement it yourself, go ahead and send a PR and I'll gladly take a look.

# Enjoy!
