import pandas as pd
from item import Item
import os
import pickle
import asyncio

import discord
from discord.ext import commands, tasks

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.basic_traders_items = self.get_items(1)
        self.black_market_items  = self.get_items(2)
        self.high_tier_items     = self.get_items(3)
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
                            
        self.ids = (140976154512326656, 182639405159153664, 275667331009478667)

    def get_items(self, sheet_name):
        df = self.get_dataframe(sheet_name)
        
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
        
    def get_dataframe(self, sheet_name):
        try:
            df =  pickle.load(open(f"trader_data_{sheet_name}.pickle", "rb"))
        except:
            df = pd.read_excel("Trader.xlsx", sheet_name,  usecols="B:C,D,E,G:H,I,J,L:M,N,O,Q:R,S,T")
            pickle.dump(df, open(f"trader_data_{sheet_name}.pickle", "wb"))
        return df

    def search_traders(self, name):
        basic_items = [item for item in self.basic_traders_items if name in item.name.lower().strip()]
        black_items = [item for item in self.black_market_items if name in item.name.lower().strip()]
        hightier_items = [item for item in self.high_tier_items if name in item.name.lower().strip()]
        drug_items = [item for item in self.drugs if name.lower() in item.name.lower()]
        
        return (basic_items, black_items, hightier_items, drug_items)
        
    async def print_list(self, trader, list, ctx):
        embed = discord.Embed(title= f"**{trader}**", color=0x09dee1)
        for item in list:
            embed.add_field(name=item.name, value = f"Buy: **{item.buy}**  ||  Sell: **{item.sell}**", inline = False)
        if list:
            ##return await ctx.send(embed=embed, delete_after= 20.0)
            try:
                return await ctx.send(embed=embed)
            except:
                return None
        return None
    
    async def delete_countdown(self, ctx, delay):
        embed = discord.Embed(color = 0xDF0000)
        embed.set_footer(text = f"Deleting query in {delay} seconds")
        delete_msg = await ctx.send(embed = embed)
        for i in range(delay):
            await asyncio.sleep(0.75)
            delay -= 1
            new_embed = delete_msg.embeds[0].set_footer(text = f"Deleting query in {delay} seconds")
            await delete_msg.edit(embed = new_embed)
        await delete_msg.edit(delete_after=0.0)
        #await ctx.message.edit(delete_after=0.0)
        
    async def output_results(self, *args, ctx):
        traders = ("Green Mountain / Green Forest", "Altar Black Market", "High Tier Military Trader", "Drugs Trader")
        msgs_sent = []
        for trader, results in zip(traders, args):
            if results:
                msg = await self.print_list(trader, results, ctx)
                if msg:
                    msgs_sent.append(msg)
        #could just use message.delete(delay)
        if msgs_sent == []:
            await ctx.send(f"Sorry {ctx.author.mention}, I couldn't find anything.")
        else:
            pass
            #self.bot.loop.create_task(self.delete_countdown(ctx, 15))
        
    @commands.command(aliases=['p', 'search', 'cost'])
    async def price(self, ctx, *args):
        """Quickly get trader prices."""
        name = " ".join(args)
        if len(args) > 0:
            await self.output_results(*self.search_traders(name.lower().strip()), ctx=ctx)   
            
    @commands.command()
    async def dfm(self, ctx):
        """Send a warning message that the bot's going offline."""
        if ctx.message.author.id in self.ids:
            await ctx.send("I'm going down for maintenance. Be back soon!")
        
    # @commands.command()
    # async def test(self, ctx):
        # try:
            # self.bot.loop.create_task(self.slow_count.start("hi"))
        # except:
            # pass
        
    # @tasks.loop(seconds=1, count=5)
    # async def slow_count(self, msg):
        # print(self.slow_count.current_loop, msg)

    # @slow_count.after_loop
    # async def after_slow_count(self):
        # print('done!')

    