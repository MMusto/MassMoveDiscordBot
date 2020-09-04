import asyncio
import discord
from discord.ext import commands
import math

PASTE_SERVER_ID     = 744359979150213212
WATCH_CHANNEL_ID    = 744659204773511239
MENTION_ROLE        = 744384313025363978
CONTROL_ID          = 747324151642980433
SPOTS = (("Base", (7672,0,12114)), ("High Tier", (6900,0,11400)), ("Troitskoe", (7912,0,14686)), ("NWAF Barracks", (4535,0,9607)), ("VMC", (4502,0,8284)), ("North NWAF", (4100,0,11200)), ("NEAF", (12100,0,12500)), ("Drug Trader", (2000,0,9800)), ("Tisy", (1650,0,14000)))

def ifl(n):
    return int(float(n))
    
class Location():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    async def update(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dist(self, x, y, z):
        return math.sqrt((self.x-x)**2 + (self.z-z)**2)

class AdminAlert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = None
        
    async def init(self):
        self.paste_server = self.bot.get_guild(PASTE_SERVER_ID)
        self.watch_channel = self.paste_server.get_channel(WATCH_CHANNEL_ID)
        self.mention = self.paste_server.get_role(MENTION_ROLE).mention
        
        self.control_channel = self.paste_server.get_channel(CONTROL_ID)
        name, loc, r = self.get_from_topic()
        self.location = loc
        self.lstr = name
        self.radius = r
        await self.control_channel.purge(limit = 10)
        e = discord.Embed(title = "**Locations**")
        for i,s in enumerate(SPOTS, 1):
            e.add_field(name = f"**{i}**", value = s[0])
        e.set_footer(text="Use 'location X Y NAME' command to set custom locations.")
        await self.control_channel.send(embed = e)
        self.controller = await self.control_channel.send(embed = self.get_embed(name, loc, r))
        
        await self.controller.add_reaction("🏠")
        await self.controller.add_reaction("◀️")
        await self.controller.add_reaction("▶️")
        await self.controller.add_reaction("🔼")
        await self.controller.add_reaction("🔽")
        #await self.update_embed()
        
    def get_embed(self, name, location, radius):
        embed = discord.Embed(title = "**ADMIN ALERTS**")
        embed.add_field(name = "Current Location:", value = f"**{name}**", inline=False)
        embed.add_field(name = "Coordinates:", value = f"(**{location.x}**, **{location.z}**)", inline = False)
        embed.add_field(name = "Radius:", value = f"**{radius}**", inline = False)
        return embed
        
    async def update_embed(self, name, loc, r):
        await self.controller.edit(embed = self.get_embed(name, loc, r))
        
    async def update_topic(self):
        await self.control_channel.edit(topic = f"{self.lstr}|{self.location.x},{self.location.y},{self.location.z}|{self.radius}")
        
    def get_from_topic(self):
        name, loc, r = self.control_channel.topic.split('|')
        loc = [ifl(i) for i in loc.split(",")]
        loc = Location(*loc)
        r = int(r)
        return name, loc, r
    
    # async def update(self, name = None, loc = None, r = None):
        # print("in update")
        # if name:
            # self.lstr = name
        # if loc:
            # self.location.update(*loc)
        # if r:
            # self.radius = r
        # await self.update_topic()
        # await self.update_embed()
        
    @commands.Cog.listener()
    async def on_ready(self):
        await self.init()

    async def check(self, name, x, y, z):
        print(f"Admin ({name}) : Checking ({self.location.x}, {self.location.z}) against ({x}, {z})")
        dist = self.location.dist(x,y,z)
        dist = int(dist)
        x = int(x)
        z = int(z)
        if dist <= self.radius:
            await self.watch_channel.send(f"{self.mention} {name} ({x}, {z}) is **{dist} m** away from **{self.lstr}** ({int(self.location.x)}, {int(self.location.z)})")

    async def process(self, embed):
        name    = embed.fields[0].value
        details = embed.fields[2].value.lower()
        
        if "teleport" in details:
            if "crosshair" in details:
                coords = details.split("<")[-1][:-3]
                x,y,z = (ifl(i) for i in coords.split(","))
                await self.check(name, x,y,z)
            elif "(pos=" in details:
                coords = details.split("=")[-1][:-2]
                x,y,z = (ifl(i) for i in coords.split(","))
                await self.check(name, x,y,z)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == WATCH_CHANNEL_ID and message.author.bot:
            if message.embeds:
                for e in message.embeds:
                    if len(e.fields) >= 3:
                        await self.process(e)
    
    @commands.command()
    async def radius(self, ctx, r):
        '''Set alert radius. USAGE - .radius R'''
        try:
            self.radius = int(r)
            # await self.update_topic()
            await self.update_embed(self.lstr, self.location, int(r))
            await ctx.send(f"Radius set to **{self.radius}**.")
        except:
            await ctx.send(f"Invalid radius: {r}.")
    
    @commands.command()
    async def location(self, ctx, x, z, *name):
        '''Set custom alert center location. USAGE - .location X Y NAME'''
        try:
            if len(name) == 0:
                self.lstr = "Custom Location"
            else:
                self.lstr = " ".join(name)
                
            await self.location.update(ifl(x),0,ifl(z))
            # await self.update_topic()
            await self.update_embed(self.lstr, self.location, self.radius)
            self.index = None
            await ctx.send(f"New Alert Center: **{self.lstr}** - (**{x}**, **{z}**)")
        except:
            await ctx.send(f"Invalid coordinates: ({x}, {z}).")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user != self.bot.user and reaction.message.id == self.controller.id:
            if type(self.index) is int:
                if reaction.emoji == '🏠':
                    self.index = 0
                if reaction.emoji == "◀️":
                    self.index -= 1
                    self.index %= len(SPOTS)
                if reaction.emoji == "▶️":
                    self.index += 1
                    self.index %= len(SPOTS)
            else:
                self.index = 0
            
            new_loc = SPOTS[self.index]
            
            if reaction.emoji == "🔼":
                self.radius += 500
            if reaction.emoji == "🔽":
                self.radius -= 500
                
            self.lstr = new_loc[0]

            await self.location.update(*new_loc[1])
            # await self.update_topic()
            await self.update_embed(new_loc[0], self.location, self.radius)
            #await self.update(name = new_loc[0], loc = new_loc[1], r = new_radius)
            await reaction.message.remove_reaction(reaction.emoji, user)
            
    @commands.command()
    async def save(self, ctx):
        '''Save current alert location to persist through restarts. USAGE - .save'''
        await self.update_topic()
        
    @commands.command()
    async def test_cmd(self, ctx):
        '''should show up'''
        return
    
    