class Item:
    def __init__(self, name, buy = "N/A", sell = "N/A"):
        if "armbands" in name.lower():
            name = "Armbands"
        if type(buy) is str:
            buy = buy.strip()
        if type(sell) is str:
            sell  = sell.strip()
        if type(sell) not in (int, str):
            sell = "N/A"
        if type(buy) not in (int, str):
            buy = "N/A"
            
        self.name = name
        self.buy = buy
        self.sell = sell