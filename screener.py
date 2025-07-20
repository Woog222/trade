
# local
from coin import Coin
import config
from binance_app import BinanceApp



class Screener:
    def __init__(self):
        self.app = BinanceApp()
        self.coins = self.get_coins()
        
    def get_coins(self):
        """
        Get all coins from the exchange (USDT perpetual futures only)
        return (list): A list of Coin objects
        
        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information
        """
        c = self.app.client.exchange_info()
        symbols = [x.get("symbol") for x in c.get("symbols") if x.get("quoteAsset") == "USDT" and x.get("contractType") == "PERPETUAL"]
        return [Coin(symbol) for symbol in symbols]

    def get_sorted_coins(self, key):
        """
        key : volume, price_change  
        return (list): A list of Coin objects sorted by the key
        """
        return sorted(self.coins, key=lambda x: getattr(x, key), reverse=True)[:config.SCREEN_LIMIT]
    
    
if __name__ == "__main__":
    screener = Screener()
    coins_sorted_by_volume = screener.get_sorted_coins("volume")
    coins_sorted_by_price_change = screener.get_sorted_coins("price_change")
    
    
    # 1. Update favorites
    with open("favorites.txt", "r") as f:
        old_favorites = set(f.read().splitlines())
    new_favorites = set([coin.symbol for coin in coins_sorted_by_volume]) | set([coin.symbol for coin in coins_sorted_by_price_change])
    favorites_added = new_favorites - old_favorites
    favorites_removed = old_favorites - new_favorites
    
    with open("favorites.txt", "w") as f:
        f.write("\n".join(new_favorites))
    print(f"Favorites updated to favorites.txt")
        
    # 2. Update summary
    with open("summary.txt", "w") as f:

        # 1. volume
        f.write("---------------------------------------------\nVolume\n---------------------------------------------\n")
        for coin in coins_sorted_by_volume:
            f.write(str(coin) + "\n")
        
        # 2. price change
        f.write("---------------------------------------------\nPrice Change\n---------------------------------------------\n")
        for coin in coins_sorted_by_price_change:
            f.write(str(coin) + "\n")
            
        
        # 3. Update favorites
        f.write(f"Favorites added: {favorites_added}\n")
        f.write(f"Favorites removed: {favorites_removed}\n")
            

            
    print("Summary saved to summary.txt")
            
            
    