from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from taas_api.enums import PosSide, Strategy, Side
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
    pos_side: Optional[str] = None

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
            return (
                False,
                "pair must correct syntax: {BASE}-{QUOTE} or {BASE}:{VARIANT}-{QUOTE} ex. ETH-USDT or ETH:PERP-USDT",
            )

        qty_fields = ["sell_token_amount", "base_asset_qty", "quote_asset_qty"]
        if all([getattr(self, field) is None for field in qty_fields]):
            return False, f"need one of {qty_fields}"

        if self.engine_passiveness is not None:
            if not (0 <= self.engine_passiveness <= 1):
                return False, "engine_passiveness out of range, must be [0,1]"

        if self.schedule_discretion is not None:
            if not (0.02 <= self.schedule_discretion <= 1):
                return False, "schedule_discretion out of range, must be [0.02,1]"

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
    pos_side: str = None

    def validate(self):
        try:
            Side(self.side)
        except ValueError:
            return False, "side must be 'buy' or 'sell'"

        result = re.search(INTERNAL_PAIR_RE_PATTERN, self.pair)

        if result is None:
            return (
                False,
                "pair must correct syntax: {BASE}-{QUOTE} or {BASE}:{VARIANT}-{QUOTE} ex. ETH-USDT or ETH:PERP-USDT",
            )

        if self.pos_side:
            try:
                PosSide(self.pos_side)
            except ValueError:
                return (False, "pos_side must be 'long' or 'short'")

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
            if not (0.02 <= self.schedule_discretion <= 1):
                return False, ["schedule_discretion out of range, must be [0.02,1]"]

        if self.alpha_tilt is not None:
            if not (-1 <= self.alpha_tilt <= 1):
                return False, ["alpha_tilt out of range, must be [-1,1]"]

        if self.exposure_tolerance is not None:
            if not (0.02 <= self.exposure_tolerance <= 1):
                return False, ["exposure_tolerance out of range, must be [0.02,1]"]

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


@dataclass
class OrderInChain:
    pair: str
    side: str
    base_asset_qty: float = None
    quote_asset_qty: float = None
    priority: int = None

    def validate(self):
        try:
            Side(self.side)
        except ValueError:
            return False, "side must be 'buy' or 'sell'"

        result = re.search(INTERNAL_PAIR_RE_PATTERN, self.pair)
        if result is None:
            return (
                False,
                "pair must correct syntax: {BASE}-{QUOTE} or {BASE}:{VARIANT}-{QUOTE} ex. ETH-USDT or ETH:PERP-USDT",
            )

        if self.priority is None or not isinstance(self.priority, int):
            return False, "priority must be an integer"
        if self.priority <= 0:
            return False, "priority must be a positive integer"

        return True, None


@dataclass
class PlaceChainedOrderRequest:
    accounts: List[str]
    duration: int
    strategy: str
    orders_in_chain: List[OrderInChain]
    engine_passiveness: float = None
    schedule_discretion: float = None
    alpha_tilt: float = None
    order_condition: str = None
    order_condition_expiry: str = None
    strategy_params: dict = None
    exposure_tolerance: float = None

    def validate(self):
        if len(self.orders_in_chain) < 2:
            return False, ["At least two orders are required in a chain."]

        try:
            Strategy(self.strategy)
        except ValueError:
            return False, f"Unexpected strategy {self.strategy}"

        if self.engine_passiveness is not None and not (
            0 <= self.engine_passiveness <= 1
        ):
            return False, ["engine_passiveness out of range, must be [0,1]"]

        if self.schedule_discretion is not None and not (
            0.02 <= self.schedule_discretion <= 1
        ):
            return False, ["schedule_discretion out of range, must be [0.02,1]"]

        if self.alpha_tilt is not None and not (-1 <= self.alpha_tilt <= 1):
            return False, "alpha_tilt out of range, must be [-1,1]"

        if self.exposure_tolerance is not None and not (
            0.02 <= self.exposure_tolerance <= 1
        ):
            return False, ["exposure_tolerance out of range, must be [0.02,1]"]

        if self.strategy_params is not None and not isinstance(
            self.strategy_params, dict
        ):
            return False, ["strategy_params must be a dictionary"]

        for order in self.orders_in_chain:
            valid, error = order.validate()
            if not valid:
                return False, error

        order_validations = [order.validate() for order in self.orders_in_chain]

        if any([not success for success, error in order_validations]):
            return False, [error for success, error in order_validations if not success]

        return True, []

    def to_post_body(self):
        body = {k: v for k, v in asdict(self).items() if v is not None}
        body["orders_in_chain"] = [asdict(order) for order in self.orders_in_chain]
        return body


@dataclass
class RebalanceRequest:
    account_id: str
    target_weights: Dict[str, Dict[str, float]]
    initial_balance_notional: float
    rebalance_settings: Dict
    tolerance: float = 1
    current_balance_notional: Optional[float] = None
    counter_asset: str = "USDT"
    rebalance_mode: str = "Once"
    is_floating: bool = False
    interval: Optional[int] = None
    start_date: Optional[str] = None

    def validate(self):
        if not isinstance(self.account_id, str) or not self.account_id:
            return False, ["account_id must be a non-empty string"]
        if not isinstance(self.target_weights, dict) or not self.target_weights:
            return False, ["target_weights must be a non-empty dictionary"]
        for asset, details in self.target_weights.items():
            if not re.match(INTERNAL_PAIR_RE_PATTERN, asset):
                return False, [f"Invalid asset pair format: {asset}"]

            target_weight = details.get("targetWeight")
            if not isinstance(target_weight, (int, float)) or not (
                -100 <= target_weight <= 100
            ):
                return False, [f"targetWeight for {asset} must be between -100 and 100"]
        if not (1 <= self.tolerance <= 100):
            return False, ["tolerance must be between 1 and 100"]
        if (
            not isinstance(self.initial_balance_notional, (int, float))
            or self.initial_balance_notional <= 0
        ):
            return False, ["initial_balance_notional must be a positive number"]
        if (
            self.current_balance_notional is not None
            and self.current_balance_notional <= 0
        ):
            return False, [
                "current_balance_notional must be a positive number if provided"
            ]
        if not isinstance(self.rebalance_mode, str) or self.rebalance_mode not in [
            "Once",
            "Set Frequency",
        ]:
            return False, ["rebalance_mode must be 'Once' or 'Set Frequency'"]
        if not isinstance(self.rebalance_settings, dict) or not self.rebalance_settings:
            return False, ["rebalance_settings must be a non-empty dictionary"]
        if self.rebalance_mode == "Set Frequency":
            if (
                self.interval is None
                or not isinstance(self.interval, int)
                or self.interval <= 0
            ):
                return False, [
                    "interval must be a positive integer for 'Set Frequency' mode"
                ]
            if self.start_date is not None:
                try:
                    from datetime import datetime

                    datetime.fromisoformat(self.start_date.replace("Z", "+00:00"))
                except ValueError:
                    return False, [
                        "start_date must be a valid ISO 8601 date string if provided"
                    ]

        return True, None

    def to_post_body(self):
        return {k: v for k, v in asdict(self).items() if v is not None}
