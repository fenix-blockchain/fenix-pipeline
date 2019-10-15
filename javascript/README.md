# Fenix Pipeline JavaScript SDK

The Fenix Pipeline JavaScript SDK facilitates connection to and interaction with the [Fenix Pipeline API](https://github.com/fenix-blockchain/fenix-pipeline) from any JavaScript application from either Node.JS or the browser.


## Prerequisites and Notes

The following should be considered when using the SDK:

-   The Fenix Pipeline API requires an authentication token. Tokens are currently only available to select beta customers.


## Installation

Using npm:

```shell
$ npm i --save fenix-pipeline-sdk
```

For browser usage:

```html
<script
    type="text/javascript"
    src="https://unpkg.com/fenix-pipeline-sdk"
></script>
```


## Sample Usage

The following program demonstrates the basic use of the SDK:

```javascript
// When using Node.JS, require the 'fenix-pipeline-sdk' module
// When using in the browser via unpkg.com, the library will be available as a variable with the name 'fenixPipeline'
const fenixPipeline = require('fenix-pipeline-sdk');

// read the API key from a local environment variable called `FENIX_API_KEY`
const apiKey = process.env.FENIX_API_KEY;

// create a dataSocket with the api key
const dataSocket = new fenixPipeline.RawDataSocket(apiKey);

// connect to the Fenix service
dataSocket.connect(async () => {
    // handle incoming messages
    dataSocket.onMesssage(messaage => console.log(message));

    // subscribe to the `btc-usdt` stream
    dataSocket.subscribe(
        fenixPipeline.SubscriptionTypes.tradesByMarket,
        'btc-usdt'
    );

    // just receive messages for the next 10 seconds
    await new Promise(setTimeout(() => {}, 10 * 1000));

    // unsubscribe to all streams
    dataSocket.unsubscribe(fenixPipeline.SubscriptionTypes.allTrades);

    // close the connection
    dataSocket.close();
});
```


## Detailed Documentation

The SDK consists of the `RawDataSocket` class and the `SubscriptionType` enum.

```javascript
const { RawDataSocket, SubscriptionType } = require('fenix-pipeline-sdk');
```


### RawDataSocket Class

The `RawDataSocket` class is used to connect to Fenix Pipeline API. Create a RawDataSocket by passing an API key, and then call `connect(onConnectHandler)` on the object to establish the connection:

```javascript
const dataSocket = RawDataSocket(my_api_key);

dataSocket.connect(() => {
    // on connection code...
});
```


### Subscribing to Channels

Once connected, you can call the `subscribe(subscriptionType, name)` function to subscribe to a given channel.

```javascript
dataSocket.subscribe(SubscriptionTypes.tradesByMarket, 'btc-usdt');
```


#### Trade Data

You can get trade data in three basic subscription types. Each of these types is selectable from the `SubscriptionTypes` enum:

-   `SubscriptionTypes.tradesByExchange`: all trades on any market within a certain exchange
-   `SubscriptionTypes.tradesByMarket`: all trades from any exchange associated with a specific market (such as `BTC-USDT`)
-   `SubscriptionTypes.allTrades`: every received trade regardless of market and regardless of exchange


##### All Trades

To subscribe to all trades:

```javascript
dataSocket.subscribe(SubscriptionTypes.allTrades);
```

**Note:** the `allTrades` subscription will contain a very large number of trades; ensure your code is performant and your network connection is sufficient to avoid losing data in the stream.


##### Trades by Market

To subscribe to all trades within a given market (in this example, BTC-USDT):

```javascript
dataSocket.subscribe(SubscriptionTypes.tradesByMarket, 'btc-usdt');
```


##### Trades by Exchange

To subscribe to all trades coming from a given exchange (in this example, Binance):

```javascript
dataSocket.subscribe(SubscriptionTypes.tradesByExchange, 'binance');
```


##### Subscription Response

After sending a subscription request, a message will be sent back confirming the channel has been successfully subscribed:

```javascript
dataSocket.subscribe(SubscriptionTypes.tradesByExchange, 'binance');
```

... will result in the following message being passed into the `onMessage` handler:

```javascript
{ type: 'subscribed', message: 'trades/exchange/binance' }
```

You should then begin receiving trade data from that exchange being passed into the `onMessage` handler:

If you supply an invalid channel reference:

```javascript
dataSocket.subscribe(SubscriptionTypes.tradesByMarket, 'btc-%');
```

... will result in the following message being passed into the `onMessage` handler:

```javascript
{ type: 'error', message: 'trades/market/btc-% invalid'}
```


#### Duplicate Data

Note that subscriptions may include overlapping data; for instance, if you subscribe to all trades on the BTC-USDT market and also all trades on the Binance exchange, trades that take place on Binance related to the BTC-USDT market belong to both subscriptions.

Data coming from the API may contain duplicate entities as documented in the [API reference documentation](https://github.com/fenix-blockchain/fenix-pipeline/blob/master/api/README.md). This behavior applies equally to all subscription types.


### Unsubscribing from Channels

Unsubscribing from channels is exactly like subscribing but calling the `unsubscribe()` method:

```javascript
dataSocket.unsubscribe(SubscriptionTypes.tradesByExchange, 'binance');
```

... will result in the following message being passed into the `onMessage` handler:

```javascript
{ type: 'unsubscribed', message: 'trades/exchange/binance' }
```

If you supply a reference to a channel you are not subscribed to:

```javascript
dataSocket.unsubscribe(SubscriptionTypes.tradesByMarket, 'btc-eudt');
```

... will result in the following message being passed into the `onMessage` handler:

```python
{ type: 'error', message: 'trades/market/btc-eudt not subscribed' }
```


### Data Model

Apart from `subscribe`, `unsubscribe`, and `error` messages described above, the messages passed into the `onMessage` handler will depend on the type of object being transferred. Currently only `Trade` obejcts are supported; other types will be added in the future.


#### Trade Data

Trade data will be received as an object literal with a key `type` containing the value `data` and a channel starting with `trades:`:

```javascript
{
    type: 'data',
    message: {
        channel: 'trades:btc-usdt:binance',
        data: {
            exchange: 'kucoin',
            market: 'btc-usdt',
            euid: '12345',
            direction: 'sell',
            price: 8145.35,
            quantity: 0.003646,
            timestamp: 1570588205.321,
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

Close the connection using the `close()` method:

```javascript
dataSocket.close();
```


## Support

The Fenix Pipeline JavaScript SDK is expected to work on the following contexts:

* browsers: all modern browsers that support websockets (IE 10+, Edge 12+, FF 11+, Chrome 16+, Safari 7+, Opera 12.1+, iOS Safari 6+)
* Node.JS: all current, active and mainetance LTS releases are supported: v8, v10, v12
