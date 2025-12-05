from typing import List, Dict, Optional
import requests
import logging
from urllib.parse import urljoin
import time

from taas_api import data

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(
        self,
        url: str,
        auth_token: str = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        # TAAS URL is used for development, TAAS_IP is used for real in pipeline
        self.taas_url = url
        self.auth_token = auth_token
        self._extra_headers = dict(extra_headers) if extra_headers else {}

    def post(self, path: str, data: dict):
        start_time = time.perf_counter()
        response = None
        try:
            response = requests.post(
                urljoin(self.taas_url, path), headers=self._common_headers(), json=data
            )
            return self._handle_response(response)
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            status_code = response.status_code if response is not None else "N/A"
            logger.info(f"POST {path} latency={elapsed_ms:.1f}ms status={status_code}")

    def get(self, path: str, params: dict = {}):
        start_time = time.perf_counter()
        response = None
        try:
            response = requests.get(
                urljoin(self.taas_url, path),
                headers=self._common_headers(),
                params=params,
            )
            return self._handle_response(response)
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            status_code = response.status_code if response is not None else "N/A"
            logger.info(f"GET {path} latency={elapsed_ms:.1f}ms status={status_code}")

    def delete(self, path: str):
        start_time = time.perf_counter()
        response = None
        try:
            response = requests.delete(
                urljoin(self.taas_url, path), headers=self._common_headers()
            )
            return self._handle_response(response)
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            status_code = response.status_code if response is not None else "N/A"
            logger.info(
                f"DELETE {path} latency={elapsed_ms:.1f}ms status={status_code}"
            )

    def _handle_response(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.warning(response.content)

        return response.json()

    def _common_headers(self):
        headers = {
            "Authorization": f"Token {self.auth_token}",
        }
        if self._extra_headers:
            headers.update(self._extra_headers)
        return headers


class Client(BaseClient):
    def get_order(self, order_id: str):
        return self.get(path=f"/api/order/{order_id}")

    def get_order_summary(self, order_id: str):
        return self.get(path=f"/api/order_summary/{order_id}")

    def get_balances(
        self, exchange_names: List[str] = None, account_names: List[str] = None
    ):
        params = {}
        if exchange_names:
            params["exchange_names"] = ",".join(exchange_names)
        if account_names:
            params["account_names"] = ",".join(account_names)

        return self.get(path=f"/api/balances/", params=params)

    def get_all_orders(self, request: data.GetOrderRequest):
        if not isinstance(request, data.GetOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.GetOrderRequest}")

        return self.get(path="/api/orders/", params=request.to_post_body())

    def place_multi_order(self, request: data.PlaceMultiOrderRequest):
        if not isinstance(request, data.PlaceMultiOrderRequest):
            raise ValueError(
                f"Expecting request to be of type {data.PlaceMultiOrderRequest}"
            )

        validate_success, errors = request.validate()

        if not validate_success:
            raise ValueError(str(errors))
        return self.post(path="/api/multi_orders/", data=request.to_post_body())

    def cancel_multi_order(self, order_id: str):
        return self.delete(path=f"/api/multi_order/{order_id}")

    def place_order(self, request: data.PlaceOrderRequest):
        if not isinstance(request, data.PlaceOrderRequest):
            raise ValueError(
                f"Expecting request to be of type {data.PlaceOrderRequest}"
            )

        validate_success, error = request.validate()

        if not validate_success:
            raise ValueError(error)

        return self.post(path="/api/orders/", data=request.to_post_body())

    def cancel_order(self, order_id: str):
        return self.delete(path=f"/api/order/{order_id}")

    def close_balances(
        self,
        max_notional: float,
        account_names: List[str] = None,
        preferred_strategy: str = None,
    ):
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
            raise ValueError(
                f"Expecting request to be of type {data.GetOrderMessagesRequest}"
            )

        return self.post(path="/api/order_messages/", data=request.to_post_body())

    def amend_order(self, request: data.AmendOrderRequest):
        if not isinstance(request, data.AmendOrderRequest):
            raise ValueError(
                f"Expecting request to be of type {data.AmendOrderRequest}"
            )

        return self.post(path="/api/amend_order/", data=request.to_post_body())

    def place_chained_order(self, request: data.PlaceChainedOrderRequest):
        if not isinstance(request, data.PlaceChainedOrderRequest):
            raise ValueError(
                f"Expecting request to be of type {data.PlaceChainedOrderRequest}"
            )

        validate_success, errors = request.validate()

        if not validate_success:
            raise ValueError(str(errors))
        return self.post(path="/api/chained_orders/", data=request.to_post_body())

    def set_leverage(self, request: data.SetLeverageRequest):
        if not isinstance(request, data.SetLeverageRequest):
            raise ValueError(
                f"Expecting request to be of type {data.SetLeverageRequest}"
            )

        validate_success, errors = request.validate()
        if not validate_success:
            raise ValueError(str(errors))
        return self.post(path="/api/set_leverage/", data=request.to_post_body())
