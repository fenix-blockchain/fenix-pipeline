var fenixPipeline = require('../javascript/src/index');

var apiKey = process.env.FENIX_API_KEY;
var localOnly = process.env.LOCAL_ONLY !== 'false';
var duration = process.env.DURATION || 3;

var dataSocket = new fenixPipeline.RawDataSocket(apiKey);

if (localOnly) {
  dataSocket.uri = 'ws://localhost:8765';
}

dataSocket.onMesssage(console.log);

dataSocket.connect(function() {
  dataSocket.subscribe(fenixPipeline.SubscriptionTypes.allTrades);
  setTimeout(function() {
    dataSocket.unsubscribe(fenixPipeline.SubscriptionTypes.allTrades);
    dataSocket.close();
  }, duration * 1000);
});
