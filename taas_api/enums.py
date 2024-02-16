from enum import Enum

class Strategy(Enum):
    IS = "IS"
    TWAP = "TWAP"
    VWAP = "VWAP"
    LIMIT = "Limit"
    MARKET= "Market"

class Side(Enum):
    BUY = "buy"
    SELL = "sell"
