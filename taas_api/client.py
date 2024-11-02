from typing import List
import requests
import logging
from urllib.parse import urljoin

from taas_api import data

logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, url: str, auth_token: str = None):
        # TAAS URL is used for development, TAAS_IP is used for real in pipeline
        self.taas_url = url
        self.auth_token = auth_token

    def post(self, path: str, data: dict):
        logger.info(f"POST {path}")
        return self._handle_response(
            requests.post(
                urljoin(self.taas_url, path), headers=self._common_headers(), json=data
            )
        )

    def get(self, path: str, params: dict = {}):
        logger.info(f"GET {path}")
        return self._handle_response(
            requests.get(
                urljoin(self.taas_url, path), headers=self._common_headers(), params=params
            )
        )

    def delete(self, path: str):
        logger.info(f"DELETE {path}")
        return self._handle_response(
            requests.delete(
                urljoin(self.taas_url, path), headers=self._common_headers()
            )
        )

    def _handle_response(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.warning(response.content)
            raise

        return response.json()

    def _common_headers(self):
        return {
            "Authorization": f"Token {self.auth_token}",
        }

class Client(BaseClient):
    def get_order(self, order_id: str):
        return self.get(path=f"/api/order/{order_id}")

    def get_order_summary(self, order_id: str):
        return self.get(path=f"/api/order_summary/{order_id}")

    def get_balances(self):
        return self.get(path=f"/api/balances/")

    def get_all_orders(self, request: data.GetOrderRequest):
        if not isinstance(request, data.GetOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.GetOrderRequest}")

        return self.get(path="/api/orders/", params=request.to_post_body())

    def place_multi_order(self, request: data.PlaceMultiOrderRequest):
        if not isinstance(request, data.PlaceMultiOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.PlaceMultiOrderRequest}")

        validate_success, errors = request.validate()

        if not validate_success:
            raise ValueError(str(errors))
        return self.post(path="/api/multi_orders/", data=request.to_post_body())

    def cancel_multi_order(self, order_id: str):
        return self.delete(path=f"/api/multi_order/{order_id}")

    def place_order(self, request: data.PlaceOrderRequest):
        if not isinstance(request, data.PlaceOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.PlaceOrderRequest}")

        validate_success, error = request.validate()

        if not validate_success:
            raise ValueError(error)

        return self.post(path="/api/orders/", data=request.to_post_body())

    def cancel_order(self, order_id: str):
        return self.delete(path=f"/api/order/{order_id}")

    def close_balances(self, max_notional: float, account_names: List[str] = None, preferred_strategy: str = None):
        data = {
            "max_notional": max_notional,
        }

        if account_names:
            data["account_names"] = account_names

        if preferred_strategy:
            data["preferred_strategy"] = preferred_strategy

        return self.post(path="/api/close_balances/", data=data)

    def get_order_messages(self, request: data.GetOrderMessagesRequest):
        if not isinstance(request, data.GetOrderMessagesRequest):
            raise ValueError(f"Expecting request to be of type {data.GetOrderMessagesRequest}")

        return self.post(path="/api/order_messages/", data=request.to_post_body())

    def amend_order(self, request: data.AmendOrderRequest):
        if not isinstance(request, data.AmendOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.AmendOrderRequest}")

        return self.post(path="/api/amend_order/", data=request.to_post_body())