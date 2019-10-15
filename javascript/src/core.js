'use strict';
var EventEmitter = require('events');

var defaultUri = 'wss://api.fenixblockchain.com/ws';
var apiVersion = 'beta';

var SubscriptionTypes = {};
Object.defineProperties(SubscriptionTypes, {
  tradesByMarket: {
    value: 'trades/market',
    writable: false,
    configurable: false,
    enumerable: true
  },
  tradesByExchange: {
    value: 'trades/exchange',
    writable: false,
    configurable: false,
    enumerable: true
  },
  allTrades: {
    value: 'trades/all',
    writable: false,
    configurable: false,
    enumerable: true
  }
});

function createRawDataSocket(WebSocket, log) {
  function RawDataSocket(apiKey) {
    var _this = EventEmitter.call(this) || this;
    _this.uri = defaultUri;
    _this._apiKey = apiKey;
    _this._socket = undefined;
    return _this;
  }

  function getChannelName(kind, name) {
    log('get channel name: ' + kind + ' ' + name);
    if (kind === SubscriptionTypes.allTrades) {
      if (name) {
        throw new Error('name invalid when using ALL qualifier');
      }
      return kind;
    }

    return kind + '/' + name;
  }

  function send(rawDataSocket, request, channel) {
    if (!rawDataSocket._socket) {
      throw new Error('not yet connected');
    }

    var readyState = rawDataSocket._socket.readyState;
    if (readyState > 1) {
      throw new Error('no longer connected');
    }

    if (readyState === 0) {
      rawDataSocket._socket.on('open', function sendWhenReady() {
        send(rawDataSocket, request, channel);
      });
    } else {
      var message = JSON.stringify({
        request: request,
        channel: channel
      });
      log('sending message: ' + message);
      rawDataSocket._socket.send(message);
    }
  }

  function parseJson(rawDataSocket, json) {
    try {
      return JSON.parse(json);
    } catch (error) {
      rawDataSocket.emit('error', error);
    }
  }

  function recieve(rawDataSocket, event) {
    var data = parseJson(rawDataSocket, event.data || event);
    if (!data) {
      return;
    }

    if (data.type == 'data') {
      var messageData = parseJson(rawDataSocket, data.message.data);
      if (!messageData) {
        return;
      }
      data.message.data = messageData;
    }
    rawDataSocket.emit('message', data);
  }

  function setWebSocketHandler(webSocket, eventName, handler) {
    if (webSocket.on) {
      webSocket.on(eventName, handler);
    } else {
      webSocket['on' + eventName] = handler;
    }
  }

  RawDataSocket.prototype = Object.create(EventEmitter.prototype);

  RawDataSocket.prototype.connect = function(handler) {
    if (this._socket === undefined) {
      log('connecting to: ' + this.uri);

      this._socket = new WebSocket(
        [
          this.uri,
          '?api-version=',
          apiVersion,
          '&auth-token=',
          this._apiKey
        ].join('')
      );

      if (handler) {
        this.onConnect(handler);
      }

      var self = this;
      setWebSocketHandler(this._socket, 'open', function() {
        self.emit('connect');
      });
      setWebSocketHandler(this._socket, 'close', function() {
        self.emit('close');
        self._socket = undefined;
      });
      setWebSocketHandler(this._socket, 'error', function(event) {
        self.emit('error', event.error || event || undefined);
      });
      setWebSocketHandler(this._socket, 'message', function(event) {
        recieve(self, event);
      });
    }
  };

  RawDataSocket.prototype.close = function() {
    if (this._socket && this._socket.readyState === 1) {
      this._socket.close();
    }
  };

  RawDataSocket.prototype.subscribe = function(kind, name) {
    send(this, 'subscribe', getChannelName(kind, name));
  };

  RawDataSocket.prototype.unsubscribe = function(kind, name) {
    send(this, 'unsubscribe', getChannelName(kind, name));
  };

  RawDataSocket.prototype.onMesssage = function(handler) {
    this.on('message', handler);
  };

  RawDataSocket.prototype.onConnect = function(handler) {
    this.on('connect', handler);
  };

  RawDataSocket.prototype.onClose = function(handler) {
    this.on('close', handler);
  };

  return RawDataSocket;
}

module.exports = function(Websocket, log) {
  return {
    SubscriptionTypes,
    RawDataSocket: createRawDataSocket(Websocket, log)
  };
};
