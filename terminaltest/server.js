const WebSocket = require('ws');
const express = require('express');
const http = require('http');
const os = require('os');
const pty = require('node-pty');

// Set up express server
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.static(__dirname + '/public'));

// Determine the correct shell based on platform
function getShell() {
  const platform = os.platform();
  if (platform === 'win32') {
    return 'cmd.exe'; // Use cmd.exe on Windows
  } else {
    return 'bash'; // Use bash on Linux and macOS
  }
}

// Handle WebSocket connection
wss.on('connection', (ws) => {
  console.log('New WebSocket connection established');

  // Create a pseudo-terminal with node-pty
  const shellCommand = getShell();
  const ptyProcess = pty.spawn(shellCommand, [], {
    name: 'xterm-color',
    cols: 80,
    rows: 24,
    cwd: process.env.HOME,
    env: process.env
  });

  // Send terminal data to the WebSocket client
  ptyProcess.on('data', (data) => {
    ws.send(data);
  });

  // Receive input from the WebSocket client and write it to the terminal
  ws.on('message', (message) => {
    ptyProcess.write(message);
  });

  // Handle client disconnection
  ws.on('close', () => {
    console.log('Client disconnected');
    ptyProcess.kill(); // Kill the terminal when the client disconnects
  });
});

// Start the server
server.listen(8080, () => {
  console.log('Server running on port 8080');
});
