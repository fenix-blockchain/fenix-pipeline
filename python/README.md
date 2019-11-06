# Fenix Pipeline Python SDK

The Fenix Pipeline Python SDK facilitates connection to and interaction with the [Fenix Pipeline API](https://github.com/fenix-blockchain/fenix-pipeline) from any Python application.


## Prerequisites and Notes

The following should be considered when using the SDK:

* The Fenix Pipeline API requires an authentication token. Tokens are currently only available to select beta customers.
* The Python SDK is written using `asyncio` for performance. There are not currently specific plans to add other async libraries (such as `gevent`) but this may be considered in future releases. If you need such support, contact Fenix to discuss.


## Sample Usage

The following program demonstrates the basic use of the SDK:

```python
import asyncio
import os

from fenix_pipeline import ConnectionClosed
from fenix_pipeline import RawDataSocket
from fenix_pipeline import SubscriptionTypes
from fenix_pipeline import Trade

async def simple_sample(event_loop):
    # read the API key from a local environment variable called `FENIX_API_KEY`
    socket = RawDataSocket(os.environ.get('FENIX_API_KEY'))
    # using a context manager
    async with await socket.connect(message_handler=print_messages) as subscriber:
        # subscribe to the `btc-usdt` stream
        await subscriber.subscribe(
            SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
        # just receive messages for the next 10 seconds
        await subscriber.monitor(10)
        # unsubscribe from the `btc-usdt` stream
        await subscriber.unsubscribe(
            SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
    # done

async def print_messages(item):
    if isinstance(item, Trade):
        log.info('received: %r', item)
    else:
        log.info('other message: %s', item)

event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(simple_sample(event_loop))
```


## Detailed Documentation

The SDK uses a context manager to manage connection state and an async coroutine to provide data to the user.


### RawDataSocket Context Manager

The `RawDataSocket` class provides the context manager and manages all async activity. Create a RawDataSocket by passing an API key, and then call `connect(message_handler)` on the object to establish the connection:

```python
socket = RawDataSocket(my_api_key)

# alternate, condensed version
with socket.connect(my_message_handler) as subscriber:
    # ... interact with server
    # now sleep this coroutine
    await subscriber.monitor(10)
```

**Note:** all following sections assume you are using the name `subscriber` as shown above.

Once you have a subscriber, you can check it's current connection state with the `.connected` property:

```python
if not subscriber.connected:
    # the connection has been closed
    pass
```

You can let the subscriber receive events for a prescribed amount of time or indefinitely using the `.monitor()` method:

```python
try:
    # monitor for 10 seconds
    await subscriber.monitor(timeout=10)
    # monitor indefinitely
    await subscriber.monitor()
except ConnectionClosed:
    # the connection to the API was closed unexpectedly
    pass
```

The subscriber will continue to receive data after the call to `.monitor()` returns; this is simply a convenience method to sleep the context manager while data is being received.


### Subscribing to Channels

Within the context manager, the `subscriber` object gives you methods for requesting the channels you receive.


#### Trade Data

You can get trade data in three basic subscription types. Each of these types is selectable from the `SubscriptionTypes` enum:

* `SubscriptionTypes.TRADES_BY_EXCHANGE`: all trades on any market within a certain exchange
* `SubscriptionTypes.TRADES_BY_MARKET`: all trades from any exchange associated with a specific market (such as `BTC-USDT`)
* `SubscriptionTypes.ALL_TRADES`: every received trade regardless of market and regardless of exchange


```python
from fenix_pipeline import SubscriptionType
subscription_type = SubscriptionTypes.ALL_TRADES
```


##### All Trades

To subscribe to all trades:

```python
await subscriber.subscribe(SubscriptionTypes.ALL_TRADES)
```

**Note:** the `ALL_TRADES` subscription will contain a very large number of trades; ensure your code is performant and your network connection is sufficient to avoid losing data in the stream.


##### Trades by Market

To subscribe to all trades within a given market (in this example, BTC-USDT):

```python
await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
```


##### Trades by Exchange

To subscribe to all trades coming from a given exchange (in this example, Binance):

```python
await subscriber.subscribe(SubscriptionTypes.TRADES_BY_EXCHANGE, 'binance')
```


##### Subscription Response

After sending a subscription request, a message will be sent back confirming the channel has been successfully subscribed:

```python
await subscriber.subscribe(SubscriptionTypes.TRADES_BY_EXCHANGE, 'binance')
```

... will result in the following message being passed into the `message_handler` coroutine:

```python
{'type': 'subscribed', 'message': 'trades/exchange/binance'}
```

You should then begin receiving trade data from that exchange being passed into the `message_handler` coroutine.

If you supply an invalid channel reference:

```python
await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-%')
```

... will result in the following message being passed into the `message_handler` coroutine:

```python
{'type': 'error', 'message': 'trades/market/btc-% invalid'}
```


#### Duplicate Data

Note that subscriptions may include overlapping data; for instance, if you subscribe to all trades on the BTC-USDT market and also all trades on the Binance exchange, trades that take place on Binance related to the BTC-USDT market belong to both subscriptions.

Data coming from the API may contain duplicate entities as documented in the [API reference documentation](https://github.com/fenix-blockchain/fenix-pipeline/blob/master/api/README.md). This behavior applies equally to all subscription types.


### Unsubscribing from Channels

Unsubscribing from channels is exactly like subscribing but calling the `unsubscribe()` method of `subscriber`:

```python
await subscriber.unsubscribe(SubscriptionTypes.TRADES_BY_EXCHANGE, 'binance')
```

... will result in the following message being passed into the `message_handler` coroutine:

```python
{'type': 'unsubscribed', 'message': 'trades/exchange/binance'}
```

If you supply a reference to a channel you are not subscribed to:

```python
await subscriber.unsubscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-eudt')
```

... will result in the following message being passed into the `message_handler` coroutine:

```python
{'type': 'error', 'message': 'trades/market/btc-eudt not subscribed'}
```


### Data Model

Apart from `subscribe`, `unsubscribe`, and `error` messages described above, the messages passed into the `message_handler` coroutine will depend on the type of object being transferred. Currently only `Trade` obejcts are supported; other types will be added in the future.


#### Trade Data

Trade data will be received as an object of type `fenix_pipeline.Trade`:

```python
>>> repr(trade)
Trade(id=binance:btc-usdt:189128621, timestamp=1570839641.248, exchange=binance, pair=btc-usdt, euid=189128621, price=8272.17, quantity=0.012112, direction=buy)
>>> trade.timestamp
1570839641.248
```

Trades consist of the following fields:

* `exchange`: the exchange where the trade was effected
* `market`: the market the trade encompasses
* `euid`: the unique ID as reported by the exchange for that trade
    * the combination of `exchange`, `market`, and `euid` is globally unique amongst all trades in the API
* `direction`: `buy` or `sell`
* `price`: a Python `float` representation of the price per unit of the trade
* `quantity`: a Python `float` representation of the quantity traded
* `timestamp`: a timestamp in seconds since the epoch with millisecond resolution

Trades also have a method `_key()` that gives a globally-unique key to this trade:

```python
>>> trade._key()
'binance:btc-usdt:189128621'
```


**Note:** all floats will be represented by IEEE-754 double-precision values through the PI (with 53 bits of precision, or resolution to 16 significant digits); to ensure you do not lose precision, run only on 64-bit Python implementations.

**Note:** all timestamps can be converted to a `datetime` using `datetime.datetime.utcfromtimestamp(t).astimezone(pytz.utc)`; the value above resolves to `datetime.datetime(2019, 10, 12, 10, 20, 41, 248000, tzinfo=<UTC>)`


### Closing the Connection

Exiting the context manager automatically closes the connection and cleans up all resources.


### Error Conditions

The context manager will exit and clean up any resources it is using in any of the following cases:

* an unhandled exception in user code the context of the context manager
* the socket is closed for any reason (by the server, the client, or the transport layer)

The socket will close and clean up resources it is using but the context manager will still remain open in the following case:

* the `message_handler` coroutine raises an unhandled exception

It is the responsibility of the user to ensure any exceptions in thier `message_handler` coroutine are properly handled. This behavior will be simplified in a future version of the SDK.
