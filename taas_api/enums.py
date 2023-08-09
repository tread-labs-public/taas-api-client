from enum import Enum

class Strategy(Enum):
    IS = "IS"
    TWAP = "TWAP"
    VWAP = "VWAP"
    LIMIT = "LIMIT"
    MARKET= "MARKET"

class Side(Enum):
    BUY = "buy"
    SELL = "sell"
