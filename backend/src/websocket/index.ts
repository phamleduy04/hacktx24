import { wss } from '../server';
import { WebSocket } from 'ws';

wss.on('connection', (ws: WebSocket, req) => {
    console.log('New WebSocket connection established.');

    ws.on('message', (message: string) => {
        console.log(`Received message: ${message}`);
        // You can send data back to the client
        ws.send(`You sent: ${message}`);
    });

    ws.on('close', () => {
        console.log('WebSocket connection closed.');
    });
});