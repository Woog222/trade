from binance_app import BinanceApp
import config

from datetime import datetime

def convert_unix_to_human_readable(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

class Coin:
    def __init__(self, symbol):
        self.app = BinanceApp()
        self.symbol = symbol
        self.refresh()
        
    def refresh(self):
        self.klines = self.app.client.klines(symbol=self.symbol, interval=config.SCREEN_CANDLE_INTERVAL, limit=config.SCREEN_WINDOW//5)
        self.volume = sum([float(x[7]) for x in self.klines])
        self.sorted_price_list = self.get_sorted_price_list()
        self.price_change = (self.sorted_price_list[-1][1] - self.sorted_price_list[0][1]) / self.sorted_price_list[0][1] * 100  

    def get_24h_volume(self):
        """
        Get the 24h volume of the coin
        return (float): The 24h quotevolume of the coin
        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics
        """
        a = self.app.client.ticker_24hr_price_change(symbol=self.symbol)
        if a.get("quoteVolume") is None:
            print(self.symbol)
        return float(a.get("quoteVolume", 0))
    
    def get_sorted_price_list(self):
        price_list = [(x[0], float(x[2])) for x in self.klines] + [(x[0], float(x[3])) for x in self.klines] # high, low prices within the window
        return sorted(price_list, key = lambda x: x[1])

    def __str__(self):
        return f"-------{self.symbol} ({self.volume/1000:.2f}K) {self.price_change:.2f}%-------" \
            f"\nMin price({convert_unix_to_human_readable(self.sorted_price_list[0][0])}) : {self.sorted_price_list[0][1]} - Max price({convert_unix_to_human_readable(self.sorted_price_list[-1][0])}) : {self.sorted_price_list[-1][1]}" \
            "\n---------------------------------------------"
    def __repr__(self):
        return f"-------{self.symbol} ({self.volume/1000:.2f}K) {self.price_change:.2f}%-------" \
            f"Min price({convert_unix_to_human_readable(self.sorted_price_list[0][0])}) : {self.sorted_price_list[0][1]} - Max price({convert_unix_to_human_readable(self.sorted_price_list[-1][0])}) : {self.sorted_price_list[-1][1]}"
    
    
    
    