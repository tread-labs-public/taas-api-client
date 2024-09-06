import datetime
from taas_api import (
    TaaSClient,
    PlaceOrderRequest,
    GetOrderRequest,
    CancelOrderRequest,
    GetBalancesRequest,
    ListPriceSubscriptionsRequest,
    PriceSubscribeRequest,
    PriceUnsubscribeRequest,
    GetL2PricesRequest,
    GetCombinedL2PricesRequest,
    CreateAccountRequest,
    ArchiveAccountRequest,
    GenerateApiAuthTokenRequest,
    GetOrdersWithStatsRequest,
    PlaceMultiOrderRequest,
    ChildOrder
)

# Initialize the client
api_url = "http://localhost:8000"  # Replace with your TaaS API URL
auth_token = "3182f0a84ede90cba2a549ff6fd98aaa7fe375a2"  # Replace with your API authentication token
c = TaaSClient(api_url, auth_token)

#Orders
# 1. Place Single Order
request = PlaceOrderRequest(
    accounts=["mock"],
    pair="ETH-USDT",
    side="buy",
    duration=300,
    base_asset_qty=5,
    strategy="TWAP"
)
res = c.place_order(request)
print("Place Single Order:", res)

# 2. Get All Orders
request = GetOrderRequest(
    statuses="ACTIVE,COMPLETE", 
    before="2023-07-08T00:00:00Z", 
    after="2023-06-08T00:00:00Z", 
    page=1, 
    page_size=10
)
res = c.get_all_orders(request)
print("Get All Orders:", res)

# 3. Submit an Order
request = PlaceOrderRequest(
    accounts=["mock"],
    pair="ETH-USDT",
    side="buy",
    sell_token_amount=50000.0,
    strategy="TWAP",
    duration=300,
    time_start=int(datetime.utcnow().timestamp() * 1000),
    time_end=int((datetime.utcnow() + datetime.timedelta(minutes=5)).timestamp() * 1000)
)
res = c.place_order(request)
print("Submit Order:", res)

# 4. Get Order Details
order_id = "045158ea-a252-4306-8847-1b27f8157143"
res = c.get_order(order_id)
print("Get Order Details:", res)

# 5. Cancel Order
order_id = "045158ea-a252-4306-8847-1b27f8157143"
res = c.cancel_order(order_id)
print("Cancel Order:", res)

# 6. Get Order Messages
order_ids = ["045158ea-a252-4306-8847-1b27f8157143"]
request = GetOrderMessagesRequest(order_ids=order_ids)
res = c.get_order_messages(request)
print("Get Order Messages:", res)

# 7. Amend Order
order_id = "045158ea-a252-4306-8847-1b27f8157143"
request = AmendOrderRequest(
    order_id=order_id,
    changes={
        'base_asset_qty': 100,
        'duration': 3600
    }
)
res = c.amend_order(request)
print("Amend Order:", res)

# 8. Place Multi Order
request = PlaceMultiOrderRequest(
    accounts=["mock"],
    duration=200,
    strategy="TWAP",
    exposure_tolerance=0.5,
    child_orders=[
        ChildOrder(
            pair="ETH:PERP-USDT", 
            side="sell", 
            base_asset_qty="10"
        ),
        ChildOrder(
            pair="ETH-USDT", 
            side="buy", 
            base_asset_qty="10"
        )
    ]
)
res = c.place_multi_order(request)
print("Place Multi Order:", res)

#Accounts
# 9. Get Account Balances
res = c.get_balances()
print("Get Account Balances:", res)

# 10. Create Account
request = CreateAccountRequest(
    name="my_new_account",
    api_key="<API_KEY>",
    api_secret="<API_SECRET>",
    exchange="Binance"
)
res = c.create_account(request)
print("Create Account:", res)

# 11. Archive Account
request = ArchiveAccountRequest(name="my_new_account")
res = c.archive_account(request)
print("Archive Account:", res)

#Admin
# 12. Generate API Auth Token
request = GenerateApiAuthTokenRequest()
res = c.generate_auth_token(request)
print("Generate API Auth Token:", res)

#Analytics
# 13. Get Orders with Stats
request = GetOrdersWithStatsRequest(page_size=10, page=1)
res = c.get_orders_with_stats(request)
print("Get Orders With Stats:", res)

# 14. List Price Subscriptions
res = c.list_price_subscriptions()
print("List Price Subscriptions:", res)

# 15. Add Price Subscription
request = PriceSubscribeRequest(
    pair="ADA-USDT",
    exchange="Binance"
)
res = c.add_price_subscription(request)
print("Add Price Subscription:", res)

# 16. Remove Price Subscription
request = PriceUnsubscribeRequest(
    pair="ADA-USDT",
    exchange="Binance"
)
res = c.remove_price_subscription(request)
print("Remove Price Subscription:", res)

# 17. Get L2 Prices
request = GetL2PricesRequest(
    pair="BTC-USDT",
    exchanges=["Binance", "OKX"],
    max_levels=10
)
res = c.get_l2_prices(request)
print("Get L2 Prices:", res)
