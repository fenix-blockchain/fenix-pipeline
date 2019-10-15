var http = require('http');
var path = require('path');
var fs = require('fs');

var sdk = fs.readFileSync(
  path.resolve(__dirname, '../js/dist/fenix-pipeline-sdk.js')
);
var port = 8065;
var apiKey = process.env.FENIX_API_KEY;
var localOnly = process.env.LOCAL_ONLY !== 'false';
var duration = process.env.DURATION || 3;

var html = `<!DOCTYPE html>
<html>
    <head>
        <title>Fenix Pipeline SDK Test</title>
    </head>
    <style>
    body {
        font-family: "Gill Sans", sans-serif;
        margin: 0;
        box-sizing: border-box;
    }

    .message {
        padding: 10px;
    }

    </style>
    <script type="text/javascript" src="sdk.js"></script>
    <script type="text/javascript">
        
        function writeMessage(message) {
            var newDiv = document.createElement("div"); 
            var newContent = document.createTextNode(typeof message === 'object' ? JSON.stringify(message, null, 2) : message); 
            newDiv.classList.add("message");
            newDiv.appendChild(newContent);  
            document.getElementById("main").append(newDiv)
        }

        function clearMessages() {
            var main = document.getElementById("main");
            while (main.firstChild) {
                main.removeChild(main.firstChild);
            }
        }

        window.onload = function() {
            var dataSocket = new fenixPipeline.RawDataSocket('${apiKey}');

            if (${localOnly}) {
                dataSocket.uri = 'ws://localhost:8765';
            }

            dataSocket.onMesssage(writeMessage);

            writeMessage('Connecting...');
            dataSocket.connect(function() {
                clearMessages();
                dataSocket.subscribe(fenixPipeline.SubscriptionTypes.allTrades);
                setTimeout(function() {
                    dataSocket.unsubscribe(fenixPipeline.SubscriptionTypes.allTrades);
                    setTimeout(function() {
                        dataSocket.close();
                    }, 1000);
                }, ${duration} * 1000);
            });
        }
    </script>
<body>
    <div id="main"/>
</body>
</html>`;

var server = http.createServer((req, res) => {
  if (req.url === '/sdk.js') {
    res.write(sdk);
  } else {
    res.write(html);
  }
  res.end();
});

server.listen(port);

console.log();
console.log('Browse to http://localhost:' + port + '/ to execute the test');
console.log();
console.log('(Press any key to exit)');

process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', function() {
  server.close();
  process.exit(0);
});
