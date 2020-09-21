import discord
from discord.ext import commands
from gtts import gTTS
import asyncio

class JoinSound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_mp3 = None
        self.enabled = False
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

    @commands.command(name = "setmsg")
    async def _set_join_mp3(self, ctx, *msg):
        """Set custom join message (TTS)
        """
        msg = " ".join(msg)
        if len(msg) > 0:
            mp3_name = f'custom_msg.mp3'
            tts = gTTS(msg)
            tts.save(mp3_name)
            self.join_mp3 = mp3_name
        await ctx.send("SUCCESS!", delete_after=3)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.selected_member is None:
            return
        channel = after.channel
        if channel is None:
            return
        perms = channel.guild.me.permissions_in(channel)
        if not self._check_perms(perms):
            return
        server = channel.guild

        def dc_bot(error):
            try:
                fut = asyncio.run_coroutine_threadsafe(server.voice_client.disconnect(), self.bot.loop)
                fut.result()
            except Exception as e:
                print(e)

        if member.id == self.selected_member.id:
            if server.voice_client == None:
                await channel.connect()
                audio_source = discord.FFmpegPCMAudio(self.join_mp3)
                server.voice_client.play(audio_source, after=dc_bot)