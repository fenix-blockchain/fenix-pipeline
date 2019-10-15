# API Documentation

The Fenix Pipeline API provides REST and websockets endpoints to facilitate retrieving data from the Fenix Pipeline.


## Prerequisites and Notes

The following should be considered when using the SDK:

* The Fenix Pipeline API requires an authentication token. Tokens are currently only available to select beta customers.


## Request Headers

Two headers are required on every request:

* API version
* authorization token


### Version Header

All requests to the API require a version specification. This can be passed in a header named `x-api-version`. If the values passed is currently supported, the request will continue. A `curl` example would be:

```shell
$ curl -X GET -H "x-api-version: beta" https://api.fenixblockchain.com/exchanges
```

Requests that fail the version check will return the following error:

* 412 (precondition failed): the version passed is not currently supported by the API

If using query parameters for the version, use the `api-version` parameter:

```shell
$ curl -X GET -H https://api.fenixblockchain.com/exchanges?api-version=beta
```


### Authorization Header

All requests to the API require an authentication token. This can be passed in a header named `authorization` with a value of `bearer <TOKEN VALUE>`. A `curl` example would be:

```shell
$ curl -X GET -H "authorization: bearer abc:12345" https://api.fenixblockchain.com/exchanges
```

Requests that fail authentication will return an error from the following list:

* 401 (unauthorized): the server could not find the `authorization` header or the bearer-type was not `bearer`
* 403 (forbidden): the `authorization` header was found but the token value was improperly formed or contained invalid credentials

If using query parameters for the authentication token, use the `auth-token` parameter:

```shell
$ curl -X GET -H https://api.fenixblockchain.com/exchanges?auth-token=abc:12345
```

**Note:** DO NOT USE THIS QUERY PARAMETER IN THE BROWSER. This method is vulnerable to accidental reveal to any browser extension that monitors the URLs you visit. This is a convenience only for languages that do not support headers in web requests (JavaScript WebSocket, for instance). This behavior will change in the next version of the API to support single-use, time limited authentication tokens that can be passed safely as query parameters without concern.


## REST API

The REST API contains the following endpoints:

* `/`: basic API details
* `/exchanges`: a list of exchanges currently active in the Fenix Pipeline
* `/exchanges/<name>`: details for a specific exchange
* `/markets`: a list of markets currently active in the Fenix Pipeline

**Note:** In many examples below, responses are trimmed for clarity. Trimmed data is replaced by `...` on a line by itself.


### Index

The `/` endpoint does not return data.


### Exchanges

The `/exchanges` endpoint returns a list of exchanges being actively collected by Fenix:

Request: `GET > /exchanges`

Response (trimmed):

```json
[
    {
        "name": "bibox",
        "display_name": "bibox",
        "enabled": true
    },
    {
        "name": "binance",
        "display_name": "binance",
        "enabled": true
    },
    ...
]
```


### Exchange Details

The `/exchanges/<exchange_name>` endpoint returns more details about that exchange:

Request: `GET > /exchanges/binance`

Response (trimmed):

```json
{
    "name": "binance",
    "display_name": "binance",
    "enabled": true,
    "markets": [
        "ada-bnb",
        "ada-btc",
        "ada-eth",
        ...
        "btc-busd",
        "btc-pax",
        "btc-tusd",
        "btc-usdc",
        "btc-usds",
        "btc-usdt",
        ...
        "eth-btc",
        "eth-pax",
        "eth-tusd",
        "eth-usdc",
        "eth-usdt",
        ...
    ]
}
```


### Markets

The `/markets` endpoint returns a list of markets being actively collected on at least one exchange and which exchange(s) are collecting it:

Request: `GET > /markets`

Response (trimmed):

```json
[
    {
        "name": "ada-bnb",
        "exchanges": [
            "binance"
        ]
    },
    ...
    {
        "name": "btc-busd",
        "exchanges": [
            "binance"
        ]
    },
    ...
    {
        "name": "btc-eur",
        "exchanges": [
            "bitstamp",
            "coinbase",
            "livecoin"
        ]
    },
    ...
    {
        "name": "btc-usd",
        "exchanges": [
            "bitstamp",
            "bittrex",
            "coinbase",
            "hitbtc",
            "livecoin",
            "yobit"
        ]
    },
    ...
    {
        "name": "btc-usdt",
        "exchanges": [
            "bibox",
            "binance",
            "bittrex",
            "huobi",
            "kucoin",
            "livecoin",
            "poloniex"
        ]
    },
    ...
]
```


## Websockets API

The websockets data feeds are available at `https://api.fenixblockchain.com/ws`. All messages to the socket and all responses and data from the socket are described below.


### Subscribing to Channels

Once connected, you can send a `subscribe` request to subscribe to a given channel.

```json
{"request": "subscribe", "channel": "<channel>"}
```


#### Trade Data

You can get trade data in three basic subscription types. Each of these types is selectable from the `SubscriptionTypes` enum:

-   `trades/exchange/<name>`: all trades on any market within a certain exchange
-   `trades/market/<name>`: all trades from any exchange associated with a specific market (such as `btc-usdt`)
-   `trades/all`: every received trade regardless of market and regardless of exchange


##### All Trades

To subscribe to all trades:

```json
{"request": "subscribe", "channel": "trades/all"}
```

**Note:** the `trades/all` subscription will contain a very large number of trades; ensure your code is performant and your network connection is sufficient to avoid losing data in the stream.


##### Trades by Market

To subscribe to all trades within a given market (in this example, BTC-USDT):

```json
{"request": "subscribe", "channel": "trades/market/btc-usdt"}
```


##### Trades by Exchange

To subscribe to all trades coming from a given exchange (in this example, Binance):

```json
{"request": "subscribe", "channel": "trades/exchange/binance"}
```


#### Subscription Response

After sending a subscription request, a message will be sent back confirming the channel has been successfully subscribed:

```json
{"type": "subscribed", "message": "trades/exchange/binance" }
```

You should then begin receiving trade data from that exchange in the stream (the format of this data is described later).

If you send an invalid channel reference:

```json
{"request": "subscribe", "channel": "trades/market/btc-%"}
```

... you will receive an error:

```json
{"type": "error", "message": "trades/market/btc-% invalid"}
```


### Unsubscribing from Channels

Unsubscribing from channels is exactly like subscribing but sending `unsubscribe` request:

```json
{"request": "unsubscribe", "channel": "trades/exchange/binance"}
```

After sending an unsubscribe request, a message will be sent back confirming the channel has been successfully unsubscribed:

```json
{"type": "unsubscribed", "message": "trades/exchange/binance" }
```

If you send a reference to a channel you are not subscribed to:

```json
{"request": "unsubscribe", "channel": "trades/market/btc-eudt"}
```

... you will receive an error:

```json
{"type": "error", "message": "trades/market/btc-eudt not subscribed" }
```


### Data Model

Apart from `subscribe`, `unsubscribe`, and `error` messages described above, the messages received from the API will depend on the type of object being transferred. Currently only `trade` entities are supported; other types will be added in the future.


#### Trade Data

Trade data will be received as a json package with a key `type` containing the value `data` and a channel starting with `trades:`:

```json
{
    "type": "data",
    "message": {
        "channel": "trades:btc-usdt:binance",
        "data": {
            "exchange": "kucoin",
            "market": "btc-usdt",
            "euid": "12345",
            "direction": "sell",
            "price": 8145.35,
            "quantity": 0.003646,
            "timestamp": 1570588205.321,
        },
    },
}
```

Schema notes:

-   `exchange`: the exchange where the trade was effected
-   `market`: the market the trade encompasses
-   `euid`: the unique ID as reported by the exchange for that trade
    -   the combination of `exchange`, `market`, and `euid` is globally unique amongst all trades in the API
-   `direction`: `buy` or `sell`
-   `price`: the price per unit of the trade
-   `quantity`: the quantity traded
-   `timestamp`: a timestamp in seconds since the epoch with millisecond resolution


### Closing the Connection

Close the connection by sending a `close` request:

```json
{"request": "close"}
```

**Note:** the `close` request is not required; you can alternately just close the socket.

If the server needs to terminate the connection, it will make a best-effort to send a termination message:

```json
{"type": "!", "message": "closing connection"}
```

**Note:** it is not guaranteed that this message will be successfully sent prior to a connection being terminated.


## Duplicate Data

Note that subscriptions may include overlapping data. For instance, if you subscribe to all trades on the `btc-usdt` market and also all trades on the `binance` exchange, trades that take place on Binance related to the BTC-USDT market may appear twice in the output stream. This will change in a future version of the API so that each trade will only ever appear once.

Duplicates can be recognized by comparing the unique combination of `exchange`, `market`, and `euid`; these three properties together form a natural key for each record.
