import pandas as pd
from item import Item
import os
import pickle

import discord
from discord.ext import commands

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
                if not pd.isnull(buy) and not pd.isnull(sell):
                    name = df.at[row, col]
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
        
    def print_list(self, trader, list):
        print_str = "\n"
        print_str += "-"*80
        print_str += "\n{0:^77}\n".format(trader)
        for item in list:
            print_str += "{0:^30} | Buy Price = {1:^10} | Sell Price = {2:^10}\n".format( item.name, item.buy, item.sell )
        print_str += "-"*80
        print_str += "\n"
        return print_str

    def output_results(self, *args):
        traders = ("Green Mountain / Green Forest", "Altar Black Marker", "High Tier Military Trader", "Drugs Trader")
        print_str = ""
        for trader, results in zip(traders, args):
            if results:
                print_str += self.print_list(trader, results)
        return print_str
        
    @commands.command()
    async def price(self, ctx, *args):
        name = " ".join(args)
        msg = self.output_results(*self.search_traders(name))
        await ctx.send(msg)
