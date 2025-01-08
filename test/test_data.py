from unittest import TestCase
from taas_api import (
    PlaceOrderRequest,
    PlaceMultiOrderRequest,
    ChildOrder,
    PlaceChainedOrderRequest,
    OrderInChain,
    RebalanceRequest,
)


class PlaceOrderRequestTest(TestCase):
    def _build_order_request(self, **kwargs):
        params = {
            "accounts": ["mock"],
            "pair": "ETH-USDT",
            "side": "buy",
            "duration": 300,
            "strategy": "TWAP",
            "base_asset_qty": 5,
        }

        params.update(**kwargs)
        return PlaceOrderRequest(**params)

    def test_validate_success(self):
        order_request = self._build_order_request()
        success, error = order_request.validate()

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_validate_success_all_fields(self):
        order_request = self._build_order_request(
            base_asset_qty=None,
            quote_asset_qty=20000.0,
            engine_passiveness=0.2,
            schedule_discretion=0.08,
            alpha_tilt=0.5,
            limit_price=1800.1,
            strategy_params={"reduce_only": True},
            notes="wow!!!",
            custom_order_id="abcd-efgh",
        )
        success, error = order_request.validate()

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_validate_fail_bad_side(self):
        order_request = self._build_order_request(side="wrong")
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("side" in error)

    def test_validate_fail_bad_strategy(self):
        order_request = self._build_order_request(strategy="asdf")
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("strategy" in error)

    def test_validate_fail_bad_pair(self):
        order_request = self._build_order_request(pair="ETHUSDT")
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("pair" in error)

    def test_validate_fail_missing_qty(self):
        order_request = self._build_order_request(base_asset_qty=None)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("sell_token_amount" in error)

    def test_validate_fail_engine_passiveness_out_of_range(self):
        order_request = self._build_order_request(engine_passiveness=1.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("engine_passiveness" in error)

        order_request = self._build_order_request(engine_passiveness=-0.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("engine_passiveness" in error)

    def test_validate_fail_schedule_discretion_out_of_range(self):
        order_request = self._build_order_request(schedule_discretion=1.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("schedule_discretion" in error, error)

        order_request = self._build_order_request(engine_passiveness=-0.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("engine_passiveness" in error)

    def test_validate_allow_bad_strategy_params(self):
        order_request = self._build_order_request(strategy_params="asdf")
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("strategy_params" in error)

        order_request = self._build_order_request(strategy_params={"asdf": 1})
        success, error = order_request.validate()

        self.assertTrue(success)

    def test_validate_fail_bad_pov_limit(self):
        order_request = self._build_order_request(pov_limit=0)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("pov_limit" in error)

        order_request = self._build_order_request(pov_limit=1.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("pov_limit" in error)

    def test_validate_fail_bad_pov_limit(self):
        order_request = self._build_order_request(pov_target=0)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("pov_target" in error)

        order_request = self._build_order_request(pov_target=1.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("pov_target" in error)

    def test_to_post_body(self):
        order_request = self._build_order_request(
            base_asset_qty=None,
            quote_asset_qty=20000.0,
            engine_passiveness=0.2,
            schedule_discretion=0.08,
            alpha_tilt=0.5,
            limit_price=1800.1,
            strategy_params={"reduce_only": True},
            notes="wow!!!",
            custom_order_id="abcd-efgh",
            updated_leverage=10,
            pov_limit=3.2,
            pov_target=2.1,
        )

        post_body = order_request.to_post_body()

        self.assertEqual(["mock"], post_body["accounts"])
        self.assertEqual("ETH-USDT", post_body["pair"])
        self.assertEqual("buy", post_body["side"])
        self.assertEqual(300, post_body["duration"])
        self.assertEqual("TWAP", post_body["strategy"])
        self.assertFalse("base_asset_qty" in post_body)
        self.assertFalse("sell_token_amount" in post_body)
        self.assertEqual(20000, post_body["quote_asset_qty"])
        self.assertEqual(0.2, post_body["engine_passiveness"])
        self.assertEqual(0.08, post_body["schedule_discretion"])
        self.assertEqual(0.5, post_body["alpha_tilt"])
        self.assertEqual(1800.1, post_body["limit_price"])
        self.assertEqual({"reduce_only": True}, post_body["strategy_params"])
        self.assertEqual("wow!!!", post_body["notes"])
        self.assertEqual("abcd-efgh", post_body["custom_order_id"])
        self.assertEqual(10, post_body["updated_leverage"])
        self.assertEqual(3.2, post_body["pov_limit"])
        self.assertEqual(2.1, post_body["pov_target"])


class PlaceMultiOrderRequestTest(TestCase):
    def _build_multi_order_request(self, **kwargs):
        params = {
            "accounts": ["mock"],
            "duration": 300,
            "strategy": "TWAP",
        }

        params.update(**kwargs)
        return PlaceMultiOrderRequest(**params)

    def test_validate_success(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
            ChildOrder(
                pair="ETH-USDT",
                side="buy",
                base_asset_qty="10",
            ),
        ]

        multi_order = self._build_multi_order_request(child_orders=child_orders)
        success, errors = multi_order.validate()

        self.assertEqual(True, success)
        self.assertEqual([], errors)

    def test_validate_success_all_fields(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
            ChildOrder(
                pair="ETH-USDT",
                side="buy",
                base_asset_qty="10",
            ),
        ]

        multi_order = self._build_multi_order_request(
            strategy_params={"passive_only": True},
            engine_passiveness=0.1,
            schedule_discretion=0.1,
            exposure_tolerance=0.1,
            child_orders=child_orders,
        )
        success, errors = multi_order.validate()

        self.assertEqual(True, success)
        self.assertEqual([], errors)

    def test_validate_fail_no_orders(self):
        multi_order = self._build_multi_order_request(child_orders=[])

        success, errors = multi_order.validate()

        self.assertEqual(False, success)
        self.assertTrue("No child orders" in errors[0])

    def test_validate_fail_bad_strategy(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
        ]
        multi_order = self._build_multi_order_request(
            strategy="ABCD", child_orders=child_orders
        )

        success, errors = multi_order.validate()
        self.assertEqual(False, success)
        self.assertTrue("strategy" in errors[0])

    def test_validate_fail_bad_engine_passiveness(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
        ]
        multi_order = self._build_multi_order_request(
            engine_passiveness=-1, child_orders=child_orders
        )

        success, errors = multi_order.validate()
        self.assertEqual(False, success)
        self.assertTrue("engine_passiveness" in errors[0])

    def test_validate_fail_bad_schedule_discretion(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
        ]
        multi_order = self._build_multi_order_request(
            schedule_discretion=-1, child_orders=child_orders
        )

        success, errors = multi_order.validate()
        self.assertEqual(False, success)
        self.assertTrue("schedule_discretion" in errors[0])

    def test_validate_fail_bad_alpha_tilt(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
        ]
        multi_order = self._build_multi_order_request(
            alpha_tilt=-2, child_orders=child_orders
        )

        success, errors = multi_order.validate()
        self.assertEqual(False, success)
        self.assertTrue("alpha_tilt" in errors[0])

    def test_validate_allow_bad_strategy_params(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
        ]
        multi_order = self._build_multi_order_request(
            strategy_params={"asdf": 1}, child_orders=child_orders
        )

        success, errors = multi_order.validate()
        self.assertEqual(True, success)

    def test_validate_fail_child_orders_validate(self):
        child_orders = [
            ChildOrder(
                pair="ETHUSDT",
                side="sell",
                base_asset_qty="10",
            ),
        ]
        multi_order = self._build_multi_order_request(child_orders=child_orders)

        success, errors = multi_order.validate()
        self.assertEqual(False, success)
        self.assertTrue("pair" in errors[0], errors)

    def test_to_post_body(self):
        child_orders = [
            ChildOrder(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty="10",
            ),
            ChildOrder(
                pair="ETH-USDT", side="buy", base_asset_qty="10", pos_side="long"
            ),
        ]

        multi_order = self._build_multi_order_request(
            strategy="VWAP",
            duration=180,
            accounts=["abc"],
            strategy_params={"passive_only": True},
            engine_passiveness=0.1,
            schedule_discretion=0.2,
            alpha_tilt=0.3,
            exposure_tolerance=0.4,
            child_orders=child_orders,
        )
        body = multi_order.to_post_body()

        self.assertEqual("VWAP", body["strategy"])
        self.assertEqual(180, body["duration"])
        self.assertEqual(["abc"], body["accounts"])
        self.assertEqual({"passive_only": True}, body["strategy_params"])
        self.assertEqual(0.1, body["engine_passiveness"])
        self.assertEqual(0.2, body["schedule_discretion"])
        self.assertEqual(0.3, body["alpha_tilt"])
        self.assertEqual(0.4, body["exposure_tolerance"])
        self.assertEqual("ETH:PERP-USDT", body["child_orders"][0]["pair"])
        self.assertEqual("sell", body["child_orders"][0]["side"])
        self.assertEqual("10", body["child_orders"][0]["base_asset_qty"])
        self.assertEqual("ETH-USDT", body["child_orders"][1]["pair"])
        self.assertEqual("buy", body["child_orders"][1]["side"])
        self.assertEqual("10", body["child_orders"][1]["base_asset_qty"])
        self.assertEqual("long", body["child_orders"][1]["pos_side"])


class ChildOrderTest(TestCase):
    def test_validate_success(self):
        order = ChildOrder(
            pair="ETH-USDT",
            side="sell",
            base_asset_qty="10",
        )
        success, error = order.validate()

        self.assertEqual(True, success)
        self.assertTrue(error is None)

    def test_validate_fail_bad_pair(self):
        order = ChildOrder(
            pair="ETHUSDT",
            side="sell",
            base_asset_qty="10",
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("pair" in error)

    def test_validate_fail_side_pair(self):
        order = ChildOrder(
            pair="ETH-USDT",
            side="barter",
            base_asset_qty="10",
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("side" in error)


class PlaceChainedOrderRequestTest(TestCase):
    def _build_chained_order_request(self, **kwargs):
        orders_in_chain = [
            OrderInChain(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty=10,
                priority=1,
            ),
            OrderInChain(
                pair="ETH-USDT",
                side="buy",
                base_asset_qty=10,
                priority=2,
            ),
        ]
        params = {
            "accounts": ["mock"],
            "duration": 300,
            "strategy": "TWAP",
            "orders_in_chain": orders_in_chain,
        }

        params.update(**kwargs)
        return PlaceChainedOrderRequest(**params)

    def test_validate_success(self):
        orders_in_chain = [
            OrderInChain(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty=10,
                priority=1,
            ),
            OrderInChain(
                pair="ETH-USDT",
                side="buy",
                base_asset_qty=10,
                priority=2,
            ),
        ]

        chained_order = self._build_chained_order_request(
            orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(True, success)
        self.assertEqual([], errors)

    def test_validate_success_all_fields(self):
        orders_in_chain = [
            OrderInChain(
                pair="ETH:PERP-USDT",
                side="sell",
                base_asset_qty=10,
                priority=1,
            ),
            OrderInChain(
                pair="ETH-USDT",
                side="buy",
                base_asset_qty=10,
                priority=2,
            ),
        ]
        chained_order = self._build_chained_order_request(
            orders_in_chain=orders_in_chain,
            engine_passiveness=0.5,
            schedule_discretion=0.1,
            strategy_params={"reduce_only": True},
            exposure_tolerance=0.3,
        )
        success, errors = chained_order.validate()

        self.assertEqual(True, success)
        self.assertEqual([], errors)

    def test_validate_fail_no_orders(self):
        chained_order = self._build_chained_order_request(orders_in_chain=[])
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("No orders in chain" in errors[0])

    def test_validate_fail_bad_strategy(self):
        orders_in_chain = [
            OrderInChain(pair="ETH-USDT", side="buy", base_asset_qty=10, priority=1),
        ]
        chained_order = self._build_chained_order_request(
            strategy="INVALID", orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("strategy" in errors[0])

    def test_validate_fail_bad_engine_passiveness(self):
        orders_in_chain = [
            OrderInChain(pair="ETH-USDT", side="buy", base_asset_qty=10, priority=1),
        ]
        chained_order = self._build_chained_order_request(
            engine_passiveness=-1, orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("engine_passiveness" in errors[0])

    def test_validate_fail_bad_schedule_discretion(self):
        orders_in_chain = [
            OrderInChain(pair="ETH-USDT", side="buy", base_asset_qty=10, priority=1),
        ]
        chained_order = self._build_chained_order_request(
            schedule_discretion=-1, orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("schedule_discretion" in errors[0])

    def test_validate_fail_bad_alpha_tilt(self):
        orders_in_chain = [
            OrderInChain(pair="ETH-USDT", side="buy", base_asset_qty=10, priority=1),
        ]
        chained_order = self._build_chained_order_request(
            alpha_tilt=-2, orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("alpha_tilt" in errors[0])

    def test_validate_fail_bad_exposure_tolerance(self):
        orders_in_chain = [
            OrderInChain(pair="ETH-USDT", side="buy", base_asset_qty=10, priority=1),
        ]
        chained_order = self._build_chained_order_request(
            exposure_tolerance=1.5, orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("exposure_tolerance" in errors)

        chained_order = self._build_chained_order_request(
            exposure_tolerance=0.01, orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("exposure_tolerance" in errors)

    def test_validate_fail_orders_in_chain_validation(self):
        orders_in_chain = [
            OrderInChain(pair="ETHUSDT", side="buy", base_asset_qty=10, priority=1),
        ]
        chained_order = self._build_chained_order_request(
            orders_in_chain=orders_in_chain
        )
        success, errors = chained_order.validate()

        self.assertEqual(False, success)
        self.assertFalse("pair" in errors[0])

    def test_to_post_body(self):
        chained_order = self._build_chained_order_request(
            engine_passiveness=0.5,
            schedule_discretion=0.1,
            strategy_params={"reduce_only": True},
            exposure_tolerance=0.3,
        )
        body = chained_order.to_post_body()

        self.assertEqual(["mock"], body["accounts"])
        self.assertEqual(300, body["duration"])
        self.assertEqual("TWAP", body["strategy"])
        self.assertEqual(0.5, body["engine_passiveness"])
        self.assertEqual(0.1, body["schedule_discretion"])
        self.assertEqual({"reduce_only": True}, body["strategy_params"])
        self.assertEqual(0.3, body["exposure_tolerance"])
        self.assertEqual("ETH:PERP-USDT", body["orders_in_chain"][0]["pair"])
        self.assertEqual("sell", body["orders_in_chain"][0]["side"])
        self.assertEqual(10, body["orders_in_chain"][0]["base_asset_qty"])
        self.assertEqual(1, body["orders_in_chain"][0]["priority"])


class OrderInChainTest(TestCase):
    def test_validate_success(self):
        order = OrderInChain(
            pair="ETH-USDT",
            side="sell",
            base_asset_qty="10",
            priority=1,
        )
        success, error = order.validate()

        self.assertEqual(True, success)
        self.assertTrue(error is None)

    def test_validate_fail_bad_pair(self):
        order = OrderInChain(
            pair="ETHUSDT",
            side="sell",
            base_asset_qty="10",
            priority=1,
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("pair" in error)

    def test_validate_fail_side_pair(self):
        order = OrderInChain(
            pair="ETH-USDT",
            side="barter",
            base_asset_qty="10",
            priority=1,
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("side" in error)

    def test_validate_fail_no_priorirty(self):
        order = OrderInChain(
            pair="ETH-USDT",
            side="sell",
            base_asset_qty="10",
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("priority" in error)

    def test_validate_fail_bad_priority(self):
        order = OrderInChain(
            pair="ETH-USDT",
            side="sell",
            base_asset_qty="10",
            priority=-1,
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("priority" in error)

        order = OrderInChain(
            pair="ETH-USDT",
            side="sell",
            base_asset_qty="10",
            priority=0,
        )
        success, error = order.validate()

        self.assertEqual(False, success)
        self.assertTrue("priority" in error)


class RebalanceRequestTest(TestCase):
    def _build_rebalance_request(self, **kwargs):
        params = {
            "account_id": "mock",
            "target_weights": {
                "BTC-USDT": {"targetWeight": 50.0},
                "ETH-USDT": {"targetWeight": 50.0},
            },
            "initial_balance_notional": 10000.0,
            "rebalance_mode": "Once",
            "tolerance": 1,
            "rebalance_settings": {
                "duration": 900,
                "engine_passiveness": 0.02,
                "exposure_tolerance": 0.1,
                "schedule_discretion": 0.08,
                "strategy": "TWAP",
            },
        }
        params.update(**kwargs)
        return RebalanceRequest(**params)

    def test_validate_success_with_default_tolerance(self):
        rebalance_request = self._build_rebalance_request()
        success, errors = rebalance_request.validate()

        self.assertTrue(success)
        self.assertIsNone(errors)

    def test_validate_success_all_fields(self):
        rebalance_request = self._build_rebalance_request(
            current_balance_notional=10000.0,
            counter_asset="USDT",
            rebalance_settings={
                "duration": 300,
                "engine_passiveness": 0.1,
                "schedule_discretion": 0.05,
            },
            interval=3600,
            start_date="2024-01-01T00:00:00Z",
            is_floating=True,
            tolerance=20,
        )
        success, errors = rebalance_request.validate()

        self.assertTrue(success)
        self.assertIsNone(errors)

    def test_validate_fail_invalid_pair_format(self):
        invalid_target_weights = {
            "BTCUSDT": {"targetWeight": 50.0},
        }
        rebalance_request = self._build_rebalance_request(
            target_weights=invalid_target_weights
        )
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn("Invalid asset pair format: BTCUSDT", errors)

    def test_validate_fail_out_of_range_target_weight(self):
        invalid_target_weights = {
            "ETH-USDT": {"targetWeight": 150.0},
        }
        rebalance_request = self._build_rebalance_request(
            target_weights=invalid_target_weights
        )
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn("targetWeight for ETH-USDT must be between -100 and 100", errors)

    def test_validate_fail_missing_account_id(self):
        rebalance_request = self._build_rebalance_request(account_id="")
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn("account_id must be a non-empty string", errors)

    def test_validate_fail_negative_initial_balance_notional(self):
        rebalance_request = self._build_rebalance_request(
            initial_balance_notional=-1000
        )
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn("initial_balance_notional must be a positive number", errors)

    def test_validate_fail_invalid_rebalance_mode(self):
        rebalance_request = self._build_rebalance_request(rebalance_mode="INVALID")
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn("rebalance_mode must be 'Once' or 'Set Frequency'", errors)

    def test_validate_fail_missing_interval_for_set_frequency(self):
        rebalance_request = self._build_rebalance_request(
            rebalance_mode="Set Frequency", interval=None
        )
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn(
            "interval must be a positive integer for 'Set Frequency' mode", errors
        )

    def test_validate_fail_invalid_start_date_for_set_frequency(self):
        rebalance_request = self._build_rebalance_request(
            rebalance_mode="Set Frequency",
            interval=3600,
            start_date="invalid-date",
        )
        success, errors = rebalance_request.validate()

        self.assertFalse(success)
        self.assertIn(
            "start_date must be a valid ISO 8601 date string if provided", errors
        )

    def test_validate_success_for_set_frequency(self):
        rebalance_request = self._build_rebalance_request(
            rebalance_mode="Set Frequency",
            interval=3600,
            start_date="2024-01-01T00:00:00Z",
        )
        success, errors = rebalance_request.validate()

        self.assertTrue(success)
        self.assertIsNone(errors)

    def test_to_post_body(self):
        rebalance_request = self._build_rebalance_request(
            current_balance_notional=10000.0,
            counter_asset="USDT",
            rebalance_settings={
                "duration": 300,
                "engine_passiveness": 0.1,
                "schedule_discretion": 0.05,
            },
            interval=3600,
            start_date="2024-01-01T00:00:00Z",
            is_floating=True,
            tolerance=5,
        )
        post_body = rebalance_request.to_post_body()

        self.assertEqual("mock", post_body["account_id"])
        self.assertEqual(50.0, post_body["target_weights"]["BTC-USDT"]["targetWeight"])
        self.assertEqual(5, post_body["tolerance"])
        self.assertEqual(10000.0, post_body["initial_balance_notional"])
        self.assertEqual(10000.0, post_body["current_balance_notional"])
        self.assertEqual("USDT", post_body["counter_asset"])
        self.assertEqual("Once", post_body["rebalance_mode"])
        self.assertTrue(post_body["is_floating"])
        self.assertEqual(3600, post_body["interval"])
        self.assertEqual("2024-01-01T00:00:00Z", post_body["start_date"])
