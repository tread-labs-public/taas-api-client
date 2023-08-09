# TaaS API Client

## Overview
These APIs provide a comprehensive interface to interact with a trading platform, allowing users to manage orders, view account balances, and execute various trading strategies. The endpoints are designed to facilitate the creation, retrieval, and deletion of orders, as well as the querying of account balances.

## Installation
Install as python dependency through private git repo:
```
pip install git+ssh://git@github.com:tread-labs-public/taas-api-client.git
```

## Client Setup
```
from taas_api import Client, PlaceOrderRequest

c = Client(url="http://localhost:8000", auth_token="b72ab3bcbce4423208a07f52b5aed207d5bd053e")
```

### Placing Orders

Submits a new order with specified parameters such as accounts, trading pair, side (buy/sell), sell token amount, duration, strategy, and engine passiveness. The place order endpoint has many fields with many restrictions. To simplify the call and run validations against the parameters, we provide a data object: `PlaceOrderRequest`. Every field can be interacted with like a regular attribute in Python.

(For more details on the order APIs [https://tread-labs.gitbook.io/api-docs/interacting-with-the-api/api-reference/orders
])

#### Example

```
req = PlaceOrderRequest(accounts=["mock"], pair="ETH-USDT", side="buy", duration=300, base_asset_qty=5, strategy="TWAP")
res = c.place_order(req)
print(res)
```

#### Response
```
{
    'id': 'd3ca321a-d25c-4cee-8a0f-3f74d239c90d',
    'parent_order': None,
    'created_at': '2023-08-08T23:54:07.659244Z',
    'buy_token': 'ETH',
    'sell_token': 'USDT',
    'pair': 'ETH-USDT',
    'side': 'buy',
    'sell_token_amount': '9890.25000000000000000000',
    'strategy': '6fe4ba3e-c578-45bd-824c-c523bf3c56de',
    'strategy_params': {},
    'limit_price': '-1.00000000000000000000',
    'time_start': '2023-08-08T23:54:06.300319Z',
    'time_end': '2023-08-08T23:59:06.300319Z',
    'duration': 300,
    'accounts': ['09d3144b-9359-4ec3-8772-2dd1bfb86652'],
    'account_names': ['mock'],
    'user': '2',
    'time_zone': 'UTC',
    'placements': [],
    'executed_qty': 0,
    'executed_price': None,
    'executed_notional': 0,
    'active': True,
    'status': 'ACTIVE',
    'engine_passiveness': '0.02000000000000000000',
    'schedule_discretion': '0.08000000000000000000',
    'failure_reason': '',
    'stop_price': '-1.00000000000000000000',
    'notes': '',
    'custom_order_id': '',
    'updated_leverage': None
}
```
### Get Order Details
Retrieves the details of a specific order using the order ID.

```
c.get_order("045158ea-a252-4306-8847-1b27f8157143")
```

### Cancelling Active Orders
Cancels a specific order using the order ID.

```
c.cancel_order("045158ea-a252-4306-8847-1b27f8157143")
```

### Getting Account Balances
For details on response structure, refer to:

https://app.gitbook.com/o/C8XGL8z2Uu1hY4jrLgyP/s/N4wz3ULyGM1MIPJxCbK1/interacting-with-the-api/api-reference/accounts

#### Example

```
res = c.get_balances()

print(res)
```

```
{
    'test': {
        'exchange': 'OKX',
        'assets': [
            {
                'symbol': 'BTC',
                'size': 3.0,
                'notional': 89409.0,
                'market_type': 'unified',
                'asset_type': 'token',
                'unrealized_profit': 0.0,
                'initial_margin': 0.0,
                'maint_margin': 0.0,
                'margin_balance': 3.0,
                'leverage': None,
                'notional_pct_total': 0.438558
            },
            {
                'symbol': 'USDT',
                'size': 8930.5901255465,
                'notional': 8930.5901255465,
                'market_type': 'unified',
                'asset_type': 'token',
                'unrealized_profit': -47.43906302083299,
                'initial_margin': 37.148328685,
                'maint_margin': 28.57563745,
                'margin_balance': 8883.151062525667,
                'leverage': None,
                'notional_pct_total': 0.043805
            },
            {
                'symbol': 'ETH:PERP-USDT',
                'size': -181.0,
                'notional': -33618.397,
                'market_type': 'perp',
                'asset_type': 'position',
                'unrealized_profit': -47.43906302083299,
                'initial_margin': 37.148328685,
                'maint_margin': 28.57563745,
                'margin_balance': 8883.151062525667,
                'leverage': 0.0,
                'notional_pct_total': 1.0
            }
        ]
    }
}
```


