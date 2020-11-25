from discord.ext import tasks, commands
from random import randint, uniform
import asyncio

def shaker_check():
    def predicate(ctx):
        return ctx.message.author.id == 140976154512326656
    return commands.check(predicate)

class Shaker(commands.Cog):
    # Shaker is limited by the ratelimited API calls
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.victims = set()
        self.speed = 0.5
        self.diseased = None
        self.first = True
        self.caller_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Shaker ready :)")

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

    @commands.command(name="shakespeed", help="Set the shake speed.")
    @shaker_check()
    async def _shaker_speed(self, ctx, speed):
        try:
            speed = float(speed)
            self.shaker_loop.change_interval(seconds=speed)
            await ctx.send(f"Shaker speed set to {speed}s")
        except ValueError:
            await ctx.send(f"Failed to set shaker speed to {speed}")

    @commands.command(name="add", help="Add a victim to the stirring pot.")
    @shaker_check()
    async def _shaker_add(self, ctx, name=''):
        # if it's only a number, it's probably a mention. Try to find by ID
        victim = self._get_member(ctx, name)

        if victim is None:
            await ctx.send(f"{name} not found.")
            return

        if victim in self.victims:
            await ctx.send(f"{victim.mention} is already in the stirring pot!")
        else:
            self.victims.add(victim)
            await ctx.send(f"{victim.mention} was added to the stirring pot!")

    @commands.command(name="remove", help="Remove a victim from the stirring pot.")
    @shaker_check()
    async def _shaker_remove(self, ctx, name=''):
        # if it's only a number, it's probably a mention. Try to find by ID
        victim = self._get_member(ctx, name)

        if victim is None:
            await ctx.send(f"{name} not found.")
            return

        if victim not in self.victims:
            await ctx.send(f"{victim.mention} is not in the stirring pot!")
        else:
            self.victims.remove(victim)
            await ctx.send(f"{victim.mention} was removed from the stirring pot!")

    @commands.command(name="shake", help="Toggle the shaker muwahaha >:")
    @shaker_check()
    async def _shaker_toggle(self, ctx):
        # Might need mutex lock here?
        if not self.active:
            self.shaker_loop.start()
            self.caller_channel = ctx.author.voice.channel if ctx.author.voice else None
            await ctx.send(f"Shaking victims: {', '.join([u.mention for u in self.victims])}")
        else:
            self.shaker_loop.cancel()
            await ctx.send("Released all victims...")

        self.active = not self.active

    async def _shake(self, victim):
        if victim.voice:
            curr_channel = victim.voice.channel
            all_choices = [channel for channel in curr_channel.guild.voice_channels if channel != curr_channel and channel != self.caller_channel]
            await victim.move_to(all_choices[randint(0, len(all_choices) - 1)])

    @tasks.loop(seconds=1.0)
    async def shaker_loop(self):
        for victim in self.victims:
            await self._shake(victim)

    @commands.command(name="heal")
    async def _heal(self, ctx, name=""):
        self.dysmetria_loop.cancel()
        await ctx.send(f"{self.diseased} was cleansed by your grace.")
        self.diseased = None

    @commands.command(name="plague")
    async def _plague(self, ctx, name=""):
        victim = self._get_member(ctx, name)
        if victim:
            if self.diseased:
                await ctx.send(f"{self.diseased} was healed. {victim.mention} was given dysmetria.")
            else:
                await ctx.send(f"{victim.mention} was given dysmetria.")
            self.diseased = victim
            # if not self.dysmetria_loop.is_running():
            self.first = True
            self.dysmetria_loop.start()
        else:
            await ctx.send(f"{name} not found.")
            return

    @tasks.loop(minutes=4)
    async def dysmetria_loop(self):
        if self.diseased.voice:
            if not self.first:
                curr_channel = self.diseased.voice.channel
                all_choices = [channel for channel in curr_channel.guild.voice_channels if channel != curr_channel]
                await self.diseased.move_to(all_choices[randint(0, len(all_choices) - 1)])
                self.dysmetria_loop.change_interval(minutes=round(uniform(4, 11), 1))
            else:
                self.first = False
