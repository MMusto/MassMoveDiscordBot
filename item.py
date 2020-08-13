class Item:
    def __init__(self, name, buy = "N/A", sell = "N/A", trader = None):
        if "armbands" in name.lower():
            name = "Armbands"
        self.name = name
        if type(buy) is str:
            buy = buy.strip()
        self.buy = buy
        if type(sell) is str:
            sell  = sell.strip()
        self.sell = sell
        self.trader = trader