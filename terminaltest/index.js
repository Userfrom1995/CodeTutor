// server.js

const { spawn } = require('child_process');
const WebSocket = require('ws');
const express = require('express');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Serve static files for the front-end
app.use(express.static(__dirname + '/public'));

wss.on('connection', (ws) => {
  console.log('New WebSocket connection');

  // Start a shell process (like Bash)
  const shell = spawn('bash');

  // When the terminal outputs data, send it to the client
  shell.stdout.on('data', (data) => {
    ws.send(data.toString());
  });

  shell.stderr.on('data', (data) => {
    ws.send(data.toString());
  });

  // When receiving input from the client, send it to the terminal
  ws.on('message', (message) => {
    shell.stdin.write(message);
  });

  // Handle terminal closing
  shell.on('close', (code) => {
    console.log(`Terminal closed with code ${code}`);
    ws.close();
  });

  ws.on('close', () => {
    shell.kill(); // Kill terminal process on WebSocket disconnect
  });
});

// Start the server
const PORT = 8080;
server.listen(PORT, () => {
  console.log(`Server is listening on http://localhost:${PORT}`);
});
