# TaaS API Client

## Overview
These APIs provide a comprehensive interface to interact with a trading platform, allowing users to manage orders, view account balances, and execute various trading strategies. The endpoints are designed to facilitate the creation, retrieval, and deletion of orders, as well as the querying of account balances.

## Installation
Install as python dependency through private git repo:
```
pip install git+ssh://git@github.com:tread-labs-public/taas-api-client.git
```

## Client Setup

Make sure the URL specified is the full path to the TaaS instance (including "https://"). To get your auth_token for the client's user, [refer to the TaaS documentation](https://tread-labs.gitbook.io/api-docs/interacting-with-the-api/get-your-api-token).

```
from taas_api import Client, PlaceOrderRequest

c = Client(url="http://localhost:8000", auth_token="b72ab3bcbce4423208a07f52b5aed207d5bd053e")
```

### Placing Orders

Submits a new order with specified parameters such as accounts, trading pair, side (buy/sell), sell token amount, duration, strategy, and engine passiveness. The place order endpoint has many fields with many restrictions. To simplify the call and run validations against the parameters, we provide a data object: `PlaceOrderRequest`. Every field can be interacted with like a regular attribute in Python.

#### Example

```
req = PlaceOrderRequest(accounts=["mock"], pair="ETH-USDT", side="buy", duration=300, base_asset_qty=5, strategy="TWAP")
res = c.place_order(req)
```

| Field               | Description                                                                                      |
|---------------------|--------------------------------------------------------------------------------------------------|
| id                  | Unique identifier for the order: .                         |
| parent_order        | Indicates whether the order has a parent order; currently, only multi-orders will have a parent order ID.  |
| created_at          | Timestamp of when the order was created:                          |
| pair                | Trading pair in Tread Labs convention (base:type-quote).    |
| sell_token_amount   | Amount of the sell token.                                         |
| buy_token_amount    | Amount of the buy token (if specified instead of the sell_token_amount).                                         |
| strategy            | Identifier for the trading strategy used in the order.                                          |
| strategy_params     | Parameters for custom values in the strategy (reduce-only, post-only, etc).              |
| limit_price         | Limit price for the entire order.                                                               |
| duration            | Duration of the order in seconds.                                                               |
| accounts            | List of account identifiers associated with the order.                                          |
| account_names       | List of account names related to the order.                                                     |
| user                | User identifier associated with the order.                                                      |
| time_zone           | Timezone for the timestamps in the order.                                                       |
| placements          | List of placement information for the order.                                                    |
| executed_qty        | Quantity of the order executed in sell token's quantity.                                        |
| executed_price      | Price at which the executed quantity was transacted.                                            |
| executed_notional   | Notional value of the executed quantity.                                                        |
| active              | Indicates if the order is active.                                                               |
| status              | Current status of the order.                                                                    |
| failure_reason      | Reason for order failure, if applicable.                                                        |
| notes               | Additional notes for the order.                                                                 |
| custom_order_id     | Custom order identifier, if present.                                                            |
| updated_leverage    | Updated leverage for the order, if applicable. _This value will persist on the exchange._        |

[For more details on the order APIs](https://tread-labs.gitbook.io/api-docs/interacting-with-the-api/api-reference/orders)

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
The client call c.get_balances() is used to retrieve the balance details of a user's assets on a trading platform.

#### Example

```
res = c.get_balances()

print(res)
```

The response is a dictionary where the keys represent the account names and the values provide detailed information about the assets held in those accounts.

For the given example, the account name is 'test' and the details are as follows:

| **Key**                   | Description               |
|-------------------------------|----------------------------------------------------------------------------------------|
| **exchange**                   | The trading platform where the assets are held. In this case, it's 'OKX'.               |
| **assets**                    | A list of dictionaries, each representing a different asset or position held in the account. Each asset dictionary contains: |
| symbol                        | The identifier or ticker of the asset or position. Examples include 'BTC', 'USDT', and 'ETH:PERP-USDT'. |
| size                          | The quantity of the asset or position. This can be positive for long positions or assets held, and negative for short positions. |
| notional                      | The notional value of the asset or position.                                          |
| market_type                   | The type of market the asset or position belongs to. Examples include 'UNIFIED' and 'PERP'. |
| asset_type                    | Specifies whether the entry represents a token/coin or a trading position. Examples include 'token' and 'position'. |
| unrealized_profit             | The profit or loss that would be realized if the asset or position were to be closed at the current market price. |
| initial_margin                | [The amount of money used to open the position](https://www.binance.com/en/futures/trading-rules/quarterly/leverage-margin). |
| maint_margin                  | The minimum amount of equity that must be maintained in the margin account.            |
| margin_balance                | The total balance in the margin account after accounting for unrealized profits and losses. |
| leverage                      | The amount of leverage applied to the position. If None, it means no leverage is applied. |
| notional_pct_total     | The percentage of the notional value of the asset or position relative to the total notional value of all assets and positions in the account. |

[For details on response structure](https://tread-labs.gitbook.io/api-docs/interacting-with-the-api/api-reference/accounts)

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



