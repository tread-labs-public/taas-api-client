from unittest import TestCase
from taas_api import data

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
        return data.PlaceOrderRequest(**params)

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
        self.assertTrue("schedule_discretion" in error)

        order_request = self._build_order_request(engine_passiveness=-0.1)
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("engine_passiveness" in error)

    def test_validate_fail_bad_strategy_params(self):
        order_request = self._build_order_request(strategy_params="asdf")
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("strategy_params" in error)

        order_request = self._build_order_request(strategy_params={"asdf": 1})
        success, error = order_request.validate()

        self.assertFalse(success)
        self.assertTrue("strategy_params" in error)

    def test_to_post_body(self):
        order_request = self._build_order_request(
            base_asset_qty=None,
            quote_asset_qty=20000.0,
            engine_passiveness=0.2,
            schedule_discretion=0.08,
            limit_price=1800.1,
            strategy_params={"reduce_only": True},
            notes="wow!!!",
            custom_order_id="abcd-efgh",
            updated_leverage=10,
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
        self.assertEqual(1800.1, post_body["limit_price"])
        self.assertEqual({"reduce_only": True}, post_body["strategy_params"])
        self.assertEqual("wow!!!", post_body["notes"])
        self.assertEqual("abcd-efgh", post_body["custom_order_id"])
        self.assertEqual(10, post_body["updated_leverage"])
