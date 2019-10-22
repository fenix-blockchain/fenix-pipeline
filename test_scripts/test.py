import asyncio
import logging
import os

import websockets

from fenix_pipeline import RawDataSocket
from fenix_pipeline import SubscriptionTypes
from fenix_pipeline import Trade


log = logging.getLogger(__name__)


LOCAL_ONLY = os.environ.get('LOCAL_ONLY', 'true').lower() in ('t', 'true', '1')
API_KEY = os.environ.get('FENIX_API_KEY')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'debug')

RUN_DURATION = int(os.environ.get('DURATION', 3))

SUBSCRIPTIONS = os.environ.get('SUBSCRIPTIONS', 'trades_by_market:btc-usdt')


async def test_socket_lifecycle(event_loop):
    subscriptions = [_get_subscription_parts(s) for s in SUBSCRIPTIONS.split('/')]
    socket = RawDataSocket(API_KEY, event_loop=event_loop)
    if LOCAL_ONLY:
        socket.uri = 'ws://localhost:8765'
    message_emitter = None
    try:
        log.info('starting receiver')
        async with await socket.connect(print_messages) as subscriber:
            log.info('subscribing')
            for subscription in subscriptions:
                await subscriber.subscribe(*subscription)
            for i in range(RUN_DURATION):
                if not subscriber.connected:
                    raise websockets.ConnectionClosed
                await asyncio.sleep(1)
            log.info('unsubscribing')
            for subscription in subscriptions:
                await subscriber.unsubscribe(*subscription)
    except websockets.exceptions.ConnectionClosed:
        log.info('socket closed, exiting lifecycle loop')
    finally:
        if message_emitter and not message_emitter.done():
            log.info('awaiting message emit task')
            await asyncio.gather(message_emitter)


def _get_subscription_parts(subscription):
    values = subscription.split(':')
    return SubscriptionTypes[values[0].upper()], values[1] if values[1] else None


async def simple_sample(event_loop):
    # read the API key from a local environment variable called `FENIX_API_KEY`
    socket = RawDataSocket(os.environ.get('FENIX_API_KEY'))
    # using a context manager
    async with await socket.connect(message_handler=print_messages) as subscriber:
        # subscribe to the `btc-usdt` stream
        await subscriber.subscribe(
            SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
        # just receive messages for the next 10 seconds
        for i in range(10):
            if not subscriber.connected:
                return
            await asyncio.sleep(1)
        await asyncio.sleep(10)
        # unsubscribe from the `btc-usdt` stream
        await subscriber.unsubscribe(
            SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
    # done


async def test_channel_to_all_state_transitions(event_loop):
    socket = RawDataSocket(API_KEY, event_loop=event_loop)
    if LOCAL_ONLY:
        socket.uri = 'ws://localhost:8765'
    async with await socket.connect(message_handler=print_messages) as subscriber:
        await asyncio.sleep(1)
        await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
        await asyncio.sleep(1)
        await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdu')
        await asyncio.sleep(1)
        await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdv')
        await asyncio.sleep(1)
        await subscriber.subscribe(SubscriptionTypes.ALL_TRADES, None)
        await asyncio.sleep(1)
        await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
        await asyncio.sleep(1)
        await subscriber.unsubscribe(SubscriptionTypes.ALL_TRADES, None)
        await asyncio.sleep(1)
        await subscriber.subscribe(SubscriptionTypes.TRADES_BY_MARKET, 'btc-usdt')
        await asyncio.sleep(1)


async def print_messages(item):
    if isinstance(item, Trade):
        log.info('received: %r', item)
    else:
        log.info('other message: %s', item)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.StreamHandler())
    log_level = getattr(logging, LOG_LEVEL.upper())
    logging.getLogger('fenix').setLevel(log_level)
    log.setLevel(log_level)
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(test_socket_lifecycle(event_loop))
