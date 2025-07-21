# local
from coin import Coin
import config
from binance_app import BinanceApp


class CoinFilter:
    """
    Base class for all coin filters
    """
    def __init__(self, limit, sort_key, filter_criteria_str:str, reverse=False, exclude_key=None):
        """
        coins : list of Coin objects
        limit : int # number of coins to return
        sort_key : lambda function to sort by
        exclude_key : lambda function to exclude by
        reverse : bool # whether to sort in descending order
        filter_criteria_str : str # criteria to filter by
        """
        self.limit = limit
        self.sort_key = sort_key 
        self.reverse = reverse
        self.exclude_key = exclude_key if exclude_key is not None else lambda x: False
        self.filter_criteria_str = filter_criteria_str
        
    def filter_coins(self, coins):
        """
        coins : list of Coin objects
        return (list): A list of Coin objects sorted by the key
        """
        coins_remaining = [coin for coin in coins if not self.exclude_key(coin)]
        self._filtered_coins = sorted(coins_remaining, key=self.sort_key, reverse=self.reverse)[:self.limit]
        return self._filtered_coins
    
    def get_filtered_coins(self):
        """
        return (list): A list of Coin objects sorted by the key
        """
        if not hasattr(self, "_filtered_coins"):
            raise AssertionError("filtered_coins is not set. Please call filter_coins() first.")
        return self._filtered_coins
    
    def get_explanation(self):
        """
        return (str): A string explaining the filter
        """
        str_builder = [f"--------------{self.filter_criteria_str}--------------"] \
            + [f"{coin.symbol} : {self.sort_key(coin):.2f}" for coin in self._filtered_coins]
        return "\n".join(str_builder)
    


class Screener:
    def __init__(self, filters):
        """
        filters : list of CoinFilter objects
        """
        self.app = BinanceApp()
        self.coins = self.get_coins()
        self.filters = filters
        
    def get_coins(self):
        """
        Get all coins from the exchange (USDT perpetual futures only)
        return (list): A list of Coin objects
        
        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information
        """
        c = self.app.client.exchange_info()
        symbols = [x.get("symbol") for x in c.get("symbols") if x.get("quoteAsset") == "USDT" and x.get("contractType") == "PERPETUAL"]
        coins = [Coin(symbol) for symbol in symbols]
        return [coin for coin in coins if coin.get_24h_volume() > config.SCREEN_MIN_VOLUME] # over 30M USDT

    def screen(self):
        """
        key : volume, price_change  
        return (list): A list of Coin objects sorted by the key
        """
        
        filtered_coins = set()
        # Update summary
        with open("summary.txt", "w") as f:
            for filter in self.filters:
                filter.filter_coins(self.coins)
                f.write(filter.get_explanation()); f.write('\n')
                filtered_coins = filtered_coins | set([coin.symbol for coin in filter.get_filtered_coins()])
                
            f.write(f'\n-------------------------Total Coins ({len(filtered_coins)})--------------------\n')
            for symbol in filtered_coins:
                f.write(symbol); f.write('\n')
            
        print("Summary saved to summary.txt")
            
            

    
    
if __name__ == "__main__":
    
    def get_price_change(coin):
        return (max([float(c[2]) for c in coin.klines]) - min([float(c[3]) for c in coin.klines])) / min([float(c[3]) for c in coin.klines]) * 100

    screener = Screener(
        filters = [
            # Filter to find coins with high trading volume in the last hour            
            CoinFilter(
                limit=config.SCREEN_LIMIT, 
                sort_key=lambda x: sum([float(candle[7]) for candle in x.klines]), # sum up the quote volume of the last 1h
                filter_criteria_str="1h_Volume",
                reverse=True
            ),
            # Filter to find coins with drastic price change in the last hour
            CoinFilter(
                limit=config.SCREEN_LIMIT, 
                sort_key=get_price_change,
                filter_criteria_str="1h_drastic_price_change",
                reverse=True
            ),
            # Filter to find coins with stagnant price change
            CoinFilter(
                limit=config.SCREEN_LIMIT, 
                sort_key=get_price_change,
                # exclude coins with over 500M USDT 24h volume and price change less than 1%
                exclude_key=lambda x: x.get_24h_volume() > 500000000 or get_price_change(x) < 0.01, 
                filter_criteria_str="1h_stagnant_price_change (exclude over 500M USDT 24h volume and price change less than 1%)",
                reverse=False
            ),  
        ]
    )
    screener.screen()
            
    