from unittest import TestCase
from taas_api import PlaceOrderRequest, PlaceMultiOrderRequest, ChildOrder


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
