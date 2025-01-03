import datetime
import requests
from taas_api.client import Client
from taas_api.data import (
    AmendOrderRequest,
    PlaceOrderRequest,
    PlaceMultiOrderRequest,
    ChildOrder,
    GetOrderRequest,
)

# Initialize the client
api_url = "your TaaS API URL"
auth_token = "your API authentication token"
c = Client(api_url, auth_token)


# 1. Place Single Order
def place_single_order():
    request = PlaceOrderRequest(
        accounts=["mock"],
        pair="ETH:PERP-USDT",
        side="buy",
        base_asset_qty=473.9736,
        strategy="TWAP",
        duration=900,
        engine_passiveness=0.01,
        notes="Okx_FP/1.799999999999998/0.01/0.08",
    )
    res = c.place_order(request)
    print("Place Single Order:", res)


# 2. Get All Orders
def get_all_orders():
    request = GetOrderRequest(
        status="ACTIVE,COMPLETE",
        before="2024-10-15T00:00:00Z",
        after="2024-10-10T00:00:00Z",
        page=1,
        page_size=10,
    )
    res = c.get_all_orders(request)
    print("Get All Orders:", res)


# 3. Submit an Order
def submit_order():
    request = PlaceOrderRequest(
        accounts=["mock"],
        pair="ETH-USDT",
        side="buy",
        sell_token_amount=50000.0,
        strategy="TWAP",
        duration=300,
    )
    res = c.place_order(request)
    print("Submit Order:", res)


# 4. Get Order Details
def get_order_details(order_id):
    res = c.get_order(order_id)
    print("Get Order Details:", res)


# 5. Cancel Order
def cancel_order(order_id):
    res = c.cancel_order(order_id)
    print("Cancel Order:", res)


# 7. Amend Order
def amend_order(order_id):
    request = AmendOrderRequest(
        order_id=order_id, changes={"base_asset_qty": 100, "duration": 3600}
    )
    try:
        res = c.amend_order(request)
        print("Amend Order:", res)
    except requests.exceptions.HTTPError as e:
        print(f"Failed to amend order {order_id}: {e.response.content.decode()}")


# 8. Place Multi Order
def place_multi_order():
    request = PlaceMultiOrderRequest(
        accounts=["mock"],
        duration=200,
        strategy="TWAP",
        child_orders=[
            ChildOrder(
                pair="ETH:PERP-USDT", side="buy", base_asset_qty=10, account="mock"
            ),
            ChildOrder(pair="ETH-USDT", side="sell", base_asset_qty=10, account="mock"),
        ],
    )
    res = c.place_multi_order(request)
    print("Place Multi Order:", res)
