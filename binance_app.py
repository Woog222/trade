from binance.um_futures import UMFutures

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

class BinanceApp:
    """singleton class for binance app"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = UMFutures(key=API_KEY, secret=SECRET_KEY)
        return cls._instance
    
    def __init__(self):
        pass
        

        
        
        
        