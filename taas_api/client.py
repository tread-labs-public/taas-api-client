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

    def get(self, path: str, params: dict ={}):
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
    def get_order(self, order_id):
        return self.get(path=f"/api/order/{order_id}")

    def get_balances(self):
        return self.get(path=f"/api/balances/")

    def get_orders(self):
        return self.get(path=f"/api/orders/")

    def place_multi_order(self, request: data.PlaceMultiOrderRequest):
        if not isinstance(request, data.PlaceMultiOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.PlaceMultiOrderRequest}")

        validate_success, errors = request.validate()

        if not validate_success:
            raise ValueError(str(errors))
        return self.post(path=f"/api/multi_orders/", data=request.to_post_body())

    def place_order(self, request: data.PlaceOrderRequest):
        if not isinstance(request, data.PlaceOrderRequest):
            raise ValueError(f"Expecting request to be of type {data.PlaceOrderRequest}")

        validate_success, error = request.validate()

        if not validate_success:
            raise ValueError(error)

        return self.post(path="/api/orders/", data=request.to_post_body())

    def cancel_order(self, order_id):
        return self.delete(path=f"/api/order/{order_id}")
