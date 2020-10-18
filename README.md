# Mass Move Discord Bot
A Python based Discord bot that has a plethora of features including the ability to mass move users from channel to channel with simple, fast, and easy commands or reactions.

This bot can be run from your own computer or a dedicated host such as Heroku (This is how I run the bot 24/7 for free). 

Requirements are as follows:
1. Discord.py API wrapper found here: [Link](https://github.com/Rapptz/discord.py)
2. Python 3.7.3+ (https://www.python.org/downloads/release/python-373/)
3. A Discord app. (You can create one [here](https://discordapp.com/developers/applications/))

## Setup
First, you need to retrieve the token assigned to your Discord app. (see below)
Replace TOKEN with your own Discord bot's token in the **bot.py** module.

`TOKEN = 'YOUR_TOKEN_HERE'`

![token from discord dev portal](https://i.imgur.com/Ubh0LKy.png)

Next, the **massmove.py** module is where the main mass move features are. At the top of this file are a few lines of config. The variables you need to modify are **CONTROL_PANEL_ID and EMOJI**. The **CONTROL_PANEL_ID** is the ID of the text channel where you can mass move users with the use of reactions and **EMOJI** is the emoji used to mass move with reactions.

**NOTE: THE CONTROL PANEL CHANNEL WILL BE PURGED ON EACH BOT START UP (ALL MESSAGES WILL BE DELETED)**

`CONTROL_PANEL_ID = '123456789012345678'`

`EMOJI = '🟢'`

## Some Commands
The default command prefix is '.' which can be changed in the **bot.py** module.
* "Reset-Mass-Move" :
  * .resetmm - If you make any Discord changes while the bot is running (such as adding or removing voice channels), simply use this command to reload the control panel.
  
* "Move-Channel-to-Channel" :
  * .mcc (SRC_CHANNEL) (DEST_CHANNEL) [roles to move] -  Moves everyone from SRC_CHANNEL to DEST_CHANNEL. If roles are included, only users with the specified roles will be moved.
  
* "Move-All-Here" :
  * .mah - Moves everyone to your current voice channel 

* **And much more**

![image of mass move reaction chat](https://i.imgur.com/1ItmNWz.png)


If you have any suggestions, bug fixes, or new feature ideas, simply reach out! Or if you would like to implement it yourself, go ahead and send a PR and I'll gladly take a look.

# Enjoy!
