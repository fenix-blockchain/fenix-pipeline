import asyncio
import dataclasses
import enum
import json
import logging

import websockets


log = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Trade:

    timestamp: float
    exchange: str
    market: str
    euid: str
    price: float
    quantity: float
    direction: str

    def __str__(self):
        return f'Trade(id={self._key()})'

    def __repr__(self):
        return (
            f'Trade(id={self._key()}, '
            f'timestamp={self.timestamp}, exchange={self.exchange}, pair={self.market}, euid={self.euid}, '
            f'price={self.price}, quantity={self.quantity}, direction={self.direction})'
        )

    def _key(self):
        return f'{self.exchange}:{self.market}:{self.euid}'

    @staticmethod
    def fromdictstr(data):
        return Trade(**(json.loads(data)))


@enum.unique
class SubscriptionTypes(enum.Enum):

    TRADES_BY_MARKET = 'trades/market'
    TRADES_BY_EXCHANGE = 'trades/exchange'
    ALL_TRADES = 'trades/all'


_API_VERSION = 'beta'


class RawDataSocket:

    uri = 'wss://api.fenixblockchain.com/ws'

    def __init__(self, apikey, event_loop=None):
        super().__init__()
        self._apikey = apikey
        self._event_loop = event_loop if event_loop else asyncio.get_event_loop()

    async def connect(self, message_handler):
        extra_headers = (
            ('authorization', f'bearer {self._apikey}'),
            ('x-api-version', _API_VERSION),
        )
        log.debug('connecting to: %s', self.uri)
        self._socket = await websockets.connect(self.uri, extra_headers=extra_headers)
        self._message_handler = message_handler
        return self

    async def subscribe(self, kind, name):
        log.debug('subscribing: %s/%s', kind.name, name)
        channel = await self._get_channel_name(kind, name)
        await self._send(dict(request='subscribe', channel=channel))

    async def unsubscribe(self, kind, name):
        log.debug('unsubscribing: %s/%s', kind.name, name)
        channel = await self._get_channel_name(kind, name)
        await self._send(dict(request='unsubscribe', channel=channel))

    async def _close(self):
        await self._send(dict(request='close'))
        await self._socket.close()
        self._socket = None

    async def _send(self, message):
        log.debug('sending message: %s', message)
        await self._socket.send(json.dumps(message))

    async def _receive(self):
        handler = self._message_handler
        try:
            async for message in self._socket:
                data = json.loads(message)
                if data['type'] == 'data':
                    data = Trade.fromdictstr(data['message']['data'])
                await handler(data)
        except Exception as e:
            log.exception(e)
            await self._close()

    async def _get_channel_name(self, kind, name=None):
        log.debug('get channel name: %s %s', kind, name)
        if kind == SubscriptionTypes.ALL_TRADES:
            if name:
                raise KeyError('name invalid when using ALL qualifier')
            return kind.value
        if not name:
            raise KeyError('name invalid')
        return f'{kind.value}/{name}'

    async def __aenter__(self):
        log.debug('entering context manager')
        self._receiver_task = self._event_loop.create_task(self._receive())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        log.debug('exiting context manager')
        await self._close()
        await asyncio.gather(self._receiver_task)
