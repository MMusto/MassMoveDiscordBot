import pandas as pd
from item import Item
import os
import urllib.request
import shutil

import asyncio
import discord
from discord.ext import commands, tasks


SPEADSHEET_URL = "https://docs.google.com/feeds/download/spreadsheets/Export?key=1hN-gHW56u6Z7fts8q1uPpz7KQNM5NE18yrhjP2VZ0ZI&exportFormat=xlsx"
TRADER_FILE_PATH = "./Trader.xlsx"
TRADER_CHANNEL_ID = 496101784847122451#743576881806442537

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ids = (140976154512326656, 182639405159153664, 275667331009478667)
        self.download_trader_file()
        self.get_items()
        
    def get_items(self):
        self.basic_traders_items = self.parse_sheet(1)
        self.black_market_items  = self.parse_sheet(2)
        self.high_tier_items     = self.parse_sheet(3)
        self.drugs               = [
                                    Item(name = "Black Drug Brick", sell = 100_000),
                                    Item(name = "Blue Meth", sell = 80_000),
                                    Item(name = "Blue Candy", sell = 60_000),
                                    Item(name = "Red Candy", sell = 40_000),
                                    Item(name = "Purple Candy", sell = 20_000),
                                    Item(name = "Green Candy", sell = 10_000),
                                    Item(name = "White Candy", sell = 5_000),
                                    Item(name = "Beige Candy", sell = 2_500)
                                   ]
                          
    def download_trader_file(self):
        with urllib.request.urlopen(SPEADSHEET_URL) as response, open(TRADER_FILE_PATH, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    def parse_sheet(self, sheet_name):
        df = pd.read_excel(TRADER_FILE_PATH, sheet_name,  usecols="B:C,D,E,G:H,I,J,L:M,N,O,Q:R,S,T")
        
        df.columns = [str(i) for i in range(df.shape[1])]
        name_cols = ("0","4","8","12")
        buy_cols = {"0":"2", "4":"6","8":"10", "12":"14"}
        sell_cols = {"0":"3", "4":"7","8":"11", "12":"15"}
        drop_cols = ["1","5","9","13"]
        df = df.drop(columns = drop_cols)
        
        rows_to_drop = []
        for row in df.index:
            all_types = set()
            for col in df.columns:
                val = df.at[row,col]
                # if type(val) is str and "Info" not in val:
                all_types.add(type(val))
            if int not in all_types:
                rows_to_drop.append(row)
        df = df.drop(rows_to_drop)
            
        items = []
        for row in df.index:
            for col in name_cols:
                buy = df.at[row, buy_cols[col]]
                sell =  df.at[row, sell_cols[col]]
                
                # if pd.notna(buy) and pd.notna(sell):
                name = df.at[row, col]
                if type(name) is str and not(pd.isna(buy) and pd.isna(sell)) and not name.startswith("Info"):
                    items.append(Item(name, buy, sell))

        return items
        
    def search_traders(self, name):
        def sort_by_name(item):
            return (item.name, str(item.buy), str(item.sell))
        basic_items      = [item for item in self.basic_traders_items if name in item.name.lower().strip()]
        black_items      = [item for item in self.black_market_items if name in item.name.lower().strip()]
        hightier_items   = [item for item in self.high_tier_items if name in item.name.lower().strip()]
        drug_items       = [item for item in self.drugs if name in item.name.lower()]
        res = (basic_items, black_items, hightier_items, drug_items)
        #Don't sort drug list
        for i in res[:-1]:
            if i:
                i.sort(key = sort_by_name)
        return res
        
    def create_embed(self, trader, result, ctx):
        embed = discord.Embed(title= f"**{trader}**", color=0x09dee1)
        for item in result:
            embed.add_field(name=item.name, value = f"Buy: **{item.buy}**  ||  Sell: **{item.sell}**", inline = False)
        if result:
            return embed
        return None
    
    async def output_results(self, *results, ctx):
        traders = ("Green Mountain / Green Forest", "Altar Black Market", "High Tier Military Trader", "Drugs Trader")
        embeds = []
        for trader, result in zip(traders, results):
            if result:
                embed = self.create_embed(trader, result, ctx)
                if embed:
                    embeds.append(ctx.send(embed = embed))
        if embeds == []:
            await ctx.send(f"Sorry {ctx.author.mention}, I couldn't find anything.")
        else:
            await asyncio.gather(*embeds)
        
    @commands.command(aliases=['p', 'search', 'cost'])
    async def price(self, ctx, *args):
        """Quickly get trader prices. Alias: p, search, cost"""
        if len(args) > 0 and TRADER_CHANNEL_ID == ctx.channel.id:
            name = " ".join(args).lower().strip()
            await self.output_results(*self.search_traders(name), ctx=ctx)   
            
    @commands.command()
    async def dfm(self, ctx):
        """Send a warning message that the bot's going offline."""
        if ctx.message.author.id in self.ids:
            await ctx.send("I'm going down for maintenance. Be back soon!")
        
    @commands.command(name = "update")
    async def update(self, ctx, *args):
        """Update trader prices from Google Spreadsheet. Must be Admin or Dev."""
        #os.remove(TRADER_FILE_PATH)
        if len(args) == 1 and args[0].lower() == "prices":
            if ctx.author.id in self.ids or ctx.author.guild_permissions.administrator:
                self.download_trader_file()
                self.get_items()
                await ctx.send(embed = discord.Embed(title = "**Trader Prices Successfully Updated!**", color = 0x00f715))
            else:
                await ctx.send(f"Sorry {ctx.author.mention}, you don't have permission for that!")
        
    