from dataclasses import dataclass, asdict
from typing import List, Union
from taas_api.enums import Strategy, Side
import re

INTERNAL_PAIR_RE_PATTERN = r"([a-zA-Z0-9]+)(:\w+)?-([a-zA-Z0-9]+)"

@dataclass
class PlaceOrderRequest:
    accounts: List[str]
    pair: str
    side: str
    duration: int
    strategy: str
    sell_token_amount: Union[int, float, str] = None
    base_asset_qty: Union[int, float, str] = None
    quote_asset_qty: Union[int, float, str] = None
    engine_passiveness: float = None
    schedule_discretion: float = None
    order_condition: str = None
    order_condition_expiry: str = None
    limit_price: Union[int, float, str] = None
    strategy_params: dict = None
    notes: str = None
    custom_order_id: str = None
    updated_leverage: int = None

    def validate(self):
        try:
            Side(self.side)
        except ValueError:
            return False, "side must be 'buy' or 'sell'"

        try:
            Strategy(self.strategy)
        except ValueError:
            return False, f"unexpected strategy {self.strategy}"

        result = re.search(INTERNAL_PAIR_RE_PATTERN, self.pair)

        if result is None:
            return False, "pair must correct syntax: {BASE}-{QUOTE} or {BASE}:{VARIANT}-{QUOTE} ex. ETH-USDT or ETH:PERP-USDT"

        qty_fields = ["sell_token_amount", "base_asset_qty", "quote_asset_qty"]
        if all([getattr(self, field) is None for field in qty_fields]):
            return False, f"need one of {qty_fields}"

        if self.engine_passiveness is not None:
            if not (0 <= self.engine_passiveness <= 1):
                return False, "engine_passiveness out of range, must be [0,1]"

        if self.schedule_discretion is not None:
            if not (0 <= self.schedule_discretion <= 1):
                return False, "schedule_discretion out of range, must be [0,1]"

        valid_strategy_params = ["passive_only", "reduce_only"]

        if self.strategy_params is not None:
            if not isinstance(self.strategy_params, dict):
                return False, "strategy_params must be a dict"

            if any([key not in valid_strategy_params for key in self.strategy_params.keys()]):
                return False, f"must use valid strategy_params: {valid_strategy_params}"

        return True, None

    def to_post_body(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class ChildOrder:
    pair: str
    side: str
    base_asset_qty: Union[int, float, str] = None
    quote_asset_qty: Union[int, float, str] = None

    def validate(self):
        try:
            Side(self.side)
        except ValueError:
            return False, "side must be 'buy' or 'sell'"

        result = re.search(INTERNAL_PAIR_RE_PATTERN, self.pair)

        if result is None:
            return False, "pair must correct syntax: {BASE}-{QUOTE} or {BASE}:{VARIANT}-{QUOTE} ex. ETH-USDT or ETH:PERP-USDT"

        return True, None


@dataclass
class PlaceMultiOrderRequest:
    accounts: List[str]
    duration: int
    strategy: str
    child_orders: List[ChildOrder]
    engine_passiveness: float = None
    schedule_discretion: float = None
    order_condition: str = None
    order_condition_expiry: str = None
    strategy_params: dict = None
    exposure_tolerance: float = None

    def validate(self):
        if len(self.child_orders) == 0:
            return False, [f"No child orders declared!"]

        try:
            Strategy(self.strategy)
        except ValueError:
            return False, [f"unexpected strategy {self.strategy}"]

        if self.engine_passiveness is not None:
            if not (0 <= self.engine_passiveness <= 1):
                return False, ["engine_passiveness out of range, must be [0,1]"]

        if self.schedule_discretion is not None:
            if not (0 <= self.schedule_discretion <= 1):
                return False, ["schedule_discretion out of range, must be [0,1]"]

        if self.exposure_tolerance is not None:
            if not (0.1 <= self.exposure_tolerance <= 1):
                return False, ["schedule_discretion out of range, must be [0.1,1]"]

        valid_strategy_params = ["passive_only", "reduce_only"]

        if self.strategy_params is not None:
            if not isinstance(self.strategy_params, dict):
                return False, ["strategy_params must be a dict"]

            if any([key not in valid_strategy_params for key in self.strategy_params.keys()]):
                return False, [f"must use valid strategy_params: {valid_strategy_params}"]

        order_validations = [order.validate() for order in self.child_orders]

        if any([not success for success, error in order_validations]):
            return False, [error for success, error in order_validations if not success]

        return True, []

    def to_post_body(self):
        return {k: v for k, v in asdict(self).items() if v is not None}
