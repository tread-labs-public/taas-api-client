from enum import Enum


class Strategy(Enum):
    IS = "IS"
    TWAP = "TWAP"
    VWAP = "VWAP"
    LIMIT = "Limit"
    MARKET = "Market"
    ICEBERG = "Iceberg"


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


class PosSide(Enum):
    LONG = "long"
    SHORT = "short"


class OrderStatus(Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    FINISHER = "FINISHER"
    COMPLETE = "COMPLETE"
    CANCELED = "CANCELED"
    PAUSED = "PAUSED"
    

class MultiOrderStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    CANCELED = "CANCELED"
    PAUSED = "PAUSED"
    
