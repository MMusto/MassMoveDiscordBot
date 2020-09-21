import discord
from discord.ext import commands
from gtts import gTTS
import asyncio

class JoinSound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_mp3 = None
        self.selected_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[!] Join Messages is ready!")

    def _check_perms(self, perms):
        """Checks to see if bot has perms to connect and speak
        """
        return perms.connect and perms.speak

    def _get_member(self, ctx, name):
        result = None
        if name[3:-1].isnumeric():
            result = ctx.guild.get_member(int(name[3:-1]))
        if result is None:
            for member in ctx.guild.members:
                needle = name.lower()
                if (member.nick and needle in member.nick.lower()) or needle in member.name.lower():
                    result = member
                    break
        return result

    @commands.command(name="setperson", help="Sets person to attach join message to.")
    async def _set_selected_member(self, ctx, name):
        m = self._get_member(ctx, name)
        if m is None:
            await ctx.send(f"'{name}' was not found!")
        else:
            self.selected_member = m
            await ctx.send(f"{m.mention} is now the trigger!")

    @commands.command(name="clearjs", help="Clears custom message and trigger person")
    async def _clear(self, ctx, name):
        self.selected_member = None
        self.join_mp3 = None
        await ctx.send("JoinSound trigger and message successfully cleared!")

    async def _set_msg(self, ctx, msg):
        if len(msg) > 0:
            mp3_name = f'custom_msg.mp3'
            tts = gTTS(msg)
            tts.save(mp3_name)
            self.join_mp3 = mp3_name
            await ctx.send("SUCCESS!", delete_after=3)
        else:
            await ctx.send("INVALID MESSAGE!", delete_after=3)

    @commands.command(name = "setmsg")
    async def _set_single_message(self, ctx, *msg):
        """Set custom join message (TTS)
        """
        msg = " ".join(msg)
        await self._set_msg(ctx, msg)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        quit_conditions = (  
                            not after,
                            before and before.channel is after.channel,
                            after.afk,
                            self.selected_member is None,
                            after.channel is None, # first condition might account for this
                            not self._check_perms(after.channel.guild.me.permissions_in(after.channel))
                          )

        if any(quit_conditions):
            return

        channel = after.channel
        server = channel.guild
        def dc_bot(error):
            try:
                fut = asyncio.run_coroutine_threadsafe(server.voice_client.disconnect(), self.bot.loop)
                fut.result()
            except Exception as e:
                print(e)

        if self.selected_member and (self.selected_member.id == member.id):
            if server.voice_client == None and self.join_mp3:
                await channel.connect()
                audio_source = discord.FFmpegPCMAudio(self.join_mp3)
                server.voice_client.play(audio_source, after=dc_bot)