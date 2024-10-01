const WebSocket = require('ws');
const { spawn } = require('child_process');
const express = require('express');
const http = require('http');

// Set up express server
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.static(__dirname + '/public'));

// When a client connects to the WebSocket
wss.on('connection', (ws) => {
  console.log('New WebSocket connection established');

  // Spawn a shell process (e.g., sh for Alpine or bash for other systems)
  const shell = spawn('sh');

  // Send shell output to the WebSocket client
  shell.stdout.on('data', (data) => {
    ws.send(data.toString());
  });

  shell.stderr.on('data', (data) => {
    ws.send(data.toString());
  });

  // When the WebSocket client sends data (terminal input), write it to the shell
  ws.on('message', (message) => {
    shell.stdin.write(message);
  });

  // Handle client disconnection, cleanup
  ws.on('close', () => {
    console.log('Client disconnected');
    shell.kill(); // Close the shell when the WebSocket client disconnects
  });

  // Handle shell process exit
  shell.on('exit', (code) => {
    console.log(`Shell process exited with code ${code}`);
    ws.close();
  });

  // If an error occurs, close the WebSocket and shell
  shell.on('error', (err) => {
    console.error('Shell error:', err);
    ws.close();
  });
});

// Start the server
server.listen(8080, () => {
  console.log('Server running on port 8080');
});
