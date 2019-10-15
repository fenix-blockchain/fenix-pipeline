var WebSocket = require('ws');
var util = require('util');
var core = require('./core');
module.exports = core(WebSocket, util.debuglog('fenix'));
