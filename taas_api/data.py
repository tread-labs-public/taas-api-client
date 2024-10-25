from dataclasses import dataclass, asdict
from typing import List, Optional
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
    sell_token_amount: float = None
    base_asset_qty: float = None
    quote_asset_qty: float = None
    engine_passiveness: float = None
    schedule_discretion: float = None
    alpha_tilt: float = None
    order_condition: str = None
    order_condition_expiry: str = None
    pov_limit: float = None
    pov_target: float = None
    limit_price: float = None
    strategy_params: dict = None
    notes: str = None
    custom_order_id: str = None
    updated_leverage: int = None
    max_otc: float = None

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

        if self.alpha_tilt is not None:
            if not (-1 <= self.alpha_tilt <= 1):
                return False, "alpha_tilt out of range, must be [-1,1]"

        if self.pov_limit is not None:
            if not (0 < self.pov_limit <= 1):
                return False, "pov_limit is a ratio within (0,1]"

        if self.pov_target is not None:
            if not (0 < self.pov_target <= 1):
                return False, "pov_target is a ratio within (0,1]"
        
        if self.max_otc is not None:
            if self.max_otc <= 0:
                return False, "max_otc must be a positive value"

        if self.strategy_params is not None:
            if not isinstance(self.strategy_params, dict):
                return False, "strategy_params must be a dict"

        return True, None

    def to_post_body(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ChildOrder:
    pair: str
    side: str
    base_asset_qty: float = None
    quote_asset_qty: float = None

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
    alpha_tilt: float = None
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

        if self.alpha_tilt is not None:
            if not (-1 <= self.alpha_tilt <= 1):
                return False, ["alpha_tilt out of range, must be [-1,1]"]

        if self.exposure_tolerance is not None:
            if not (0.1 <= self.exposure_tolerance <= 1):
                return False, ["exposure_tolerance out of range, must be [0.1,1]"]

        if self.strategy_params is not None:
            if not isinstance(self.strategy_params, dict):
                return False, ["strategy_params must be a dict"]

        order_validations = [order.validate() for order in self.child_orders]

        if any([not success for success, error in order_validations]):
            return False, [error for success, error in order_validations if not success]

        return True, []

    def to_post_body(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class GetOrderMessagesRequest:
    order_ids: List[str]

    def to_post_body(self):
        return {"order_ids": self.order_ids}

@dataclass
class AmendOrderRequest:
    order_id: str
    changes: dict

    def to_post_body(self):
        return {"order_id": self.order_id, "changes": self.changes}


@dataclass
class GetOrderRequest:
    status: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

    def to_post_body(self):
        return {k: v for k, v in asdict(self).items() if v is not None}