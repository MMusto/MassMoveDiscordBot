import discord
from discord.ext import commands
import asyncio

CONTROL_PANEL_ID = 635919393179828226
EMOJI = '🟢'

def perms_to_move():
    async def predicate(ctx):
        if ctx.author.guild_permissions.move_members:
            return True
        else:
            await ctx.send(f"Sorry you don't have permissions for that, {ctx.author.mention}")
    return commands.check(predicate)

class MassMove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.control_panel = None
        self.message_to_channel = {}
                    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[!] MassMove initializing...")
        await self.init_control_panel()
        print(f"[!] MassMove initialization complete!")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.id in self.message_to_channel.values() and before.name != after.name:
            if self.control_panel:
                for mid,cid in self.message_to_channel.items():
                    if before.id == cid:
                        msg = await self.control_panel.fetch_message(mid)
                        if msg:
                            await msg.edit(f'**{after.name}**')
                        else:
                            self.error('Control panel message not found!')
                        return
            else:
                self.error('Unknown error in "on_guild_channel_update"')

    ######################################## HELPER FUNCTIONS ############################################

    # TODO: Switch to built-in logger if when expanding functionality
    def error(self, msg):
        print(f"[!] Error: {msg}")
    
    def _any_null(self, *args):
        for a in args:
            if a is None:
                return True
        return False
        
    def _get_channel(self, server, chname : str) -> discord.channel.VoiceChannel:
        '''Helper function that returns Channel object from name snippet'''
        for channel in server.channels:
            if type(channel) is discord.channel.VoiceChannel and chname.lower() in channel.name.lower():
                return channel
        return None
        
    async def _mbr_helper(self, server, role_name : str, src_channel, dst_channel) -> None:
        '''Based off mbr. Integrated for use in .mcc
            Moves all members from src to dst if member has role_name in role.name
        ''' 
        role = self._get_role(server, role_name)
        if role:
            all_members = src_channel.members
            for member in all_members:
                if role in member.roles:
                    await member.move_to(dst_channel)

    def _get_role(self, server, role_name : str) -> discord.Role:
        '''Helper function that returns Role object from name snippet'''
        for role in server.roles:
            if role_name.lower() in role.name.lower():
                return role
        return None
    ######################################## END OF HELPER FUNCTIONS ############################################

    async def init_control_panel(self) -> None:
        '''Init mass move'''

        self.control_panel = self.bot.get_channel(CONTROL_PANEL_ID)
        if not self.control_panel:
            self.error(f"Control Panel not found : {CONTROL_PANEL_ID}")
            return

        channels =  [ch for ch in self.control_panel.guild.channels if isinstance(ch, discord.channel.VoiceChannel)]

        await self.control_panel.purge(limit=None)

        for channel in sorted(channels, key = lambda ch: ch.position):
            name = "**"+channel.name+"**"
            message = await self.control_panel.send(embed = discord.Embed(title = name))
            await message.add_reaction(EMOJI)
            self.message_to_channel[message.id] = channel.id

    @commands.command()
    @perms_to_move()
    async def resetmm(self, ctx):
        '''If you make any Discord changes while the bot is running (such as adding or moving around channels), 
            simply use this command to reload the control panel.
        '''
        await self.init_control_panel()

    @commands.command()
    @perms_to_move()
    async def mg(self, ctx, game, chname):
        ''' "Move game": Moves everyone playing "game" to channel with chname in channel name '''
        server = ctx.guild
        all_members = server.members

        move_channel = self._get_channel(server, chname)
        #Moves all people to specified channel if they have game in their currently playing game
        for member in all_members:
            if(member.voice != None and member.voice.channel and not member.voice.afk and game.lower() in str(member.game).lower()):
                await member.move_to(move_channel)
        await ctx.send(f"Mass moved everyone playing {game} to {str(move_channel)}")

    @commands.command()
    @perms_to_move()
    async def mah(self, ctx):
        ''' "Move-All-Here" : Moves everyone to your current voice channel '''
        server = ctx.guild
        author = ctx.author
        all_members = server.members

        if author.voice:
            move_channel = author.voice.channel
        else:
            await ctx.send(f"You have to be in a Voice Channel to use this command, {ctx.author.mention}")
            return
        #Moves all people to author's channel
        for member in all_members:
            if(member.voice and not member.voice.afk and member != author):
                await member.move_to(move_channel)
        await ctx.send(f"Mass moved everyone to {str(move_channel)}")
        await ctx.message.delete()
            
    @commands.command()
    async def mcc(self, ctx, src_name : str, dst_name : str, *role_names):
        ''' "Move-Channel-to-Channel" : .mcc (SRC CHANNEL) (DEST CHANNEL) [ROLES TO MOVE] -  Moves everyone from SRC to DEST. If roles are included, only users with the specified roles will be moved '''
        server = ctx.message.guild
        src_channel = self._get_channel(server, src_name)
        dst_channel = self._get_channel(server, dst_name)
        
        if len(role_names) == 0:
            if self._any_null(src_channel, dst_channel):
                null_names = [name for obj, name in [(src_channel, src_name), (dst_channel, dst_name)] if obj is None]
                await ctx.send(f"Sorry, {' and '.join(null_names)} could not be found.")
                return
            lst = [member.move_to(dst_channel) for member in src_channel.members]
            await asyncio.gather(*lst)
        else:
            for role_name in role_names:
                await self._mbr_helper(server, role_name, src_channel, dst_channel)
        
    @commands.command()
    async def mbr(self, ctx, role_name: str, dst_name: str):
        ''' "Move-By-Role" : .mbr (ROLE_NAME) (DEST CHANNEL) -  Moves everyone with ROLE_NAME to DEST CHANNEL '''
        server = ctx.message.guild
        dst_channel = self._get_channel(server, dst_name)
        got_role = self._get_role(server, role_name)
        all_members = server.members

        
        if self._any_null(dst_channel, got_role):
            null_names = [name for obj, name in [(dst_channel, dst_name), (got_role, role_name)] if obj is None]
            await ctx.send(f"Sorry, {' and '.join(null_names)} could not be found.")
            return

        for member in all_members:
            if(member.voice is not None and member.voice.channel != dst_channel and not member.voice.afk):
                for role in member.roles:
                    if role == got_role:
                        await member.move_to(dst_channel)

    def reaction_add_check(self, reaction, user):
        requirements = \
        (
            user != self.bot.user,
            reaction.emoji == EMOJI,
            reaction.message.guild.get_member(user.id).guild_permissions.move_members,
            reaction.message.channel == self.control_panel,
            reaction.message.id in self.message_to_channel
        )
        return all(requirements)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if self.reaction_add_check(reaction, user):
            def check(r,u):
                return r.emoji == EMOJI and u == user and r.message.id in self.message_to_channel

            try:
                next_reaction, _ = await self.bot.wait_for('reaction_add', check = check, timeout = 3)
                dst_channel = self.bot.get_channel(self.message_to_channel[next_reaction.message.id])
            except asyncio.TimeoutError:
                await reaction.message.remove_reaction(EMOJI, user)
                return

            src_channel = self.bot.get_channel(self.message_to_channel[reaction.message.id])
            members_to_move = [member.move_to(dst_channel) for member in src_channel.members]
            await asyncio.gather(*members_to_move)
            await reaction.message.remove_reaction(EMOJI, user)
            await next_reaction.message.remove_reaction(EMOJI, user)
            print(f"{user.display_name}/{user.name} moved everyone from {src_channel.name} to {dst_channel.name}")
