import cv2
import asyncio
import websockets
import numpy as np
import base64
import requests
from queue import Queue

boxes = []

async def process_frame(buffer):
    global boxes
    try:
        response = requests.post('https://microservices.hacktx24.tech/process_image/', files={"file": buffer.tobytes()})
        if response.status_code == 200:
            return response.json()  # Update the global boxes variable
    except requests.ConnectionError:
        print("API endpoint not reachable. Using default bounding boxes.")
    return []

async def send_video(websocket, path):
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        success, frame = cam.read()
        if not success:
            print("Error: Could not read frame.")
            break
        frame_height,frame_width= frame.shape[:2]
        
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        #frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the API asynchronously
        boxes = await process_frame(buffer)

        # Draw boxes on the frame
        for item in boxes:
            x, y, w, h = item['xyxy'][0]*frame_width, item['xyxy'][1]*frame_height, item['xyxy'][2]*frame_width, item['xyxy'][3]*frame_height
            color = (0, 255, 0)  # Green
            thickness = 2
            cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), color, thickness)

        # Encode the frame for WebSocket
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send the frame to the WebSocket client
        await websocket.send(frame_base64)

    cam.release()

async def main():
    start_server = websockets.serve(send_video, 'localhost', 8000)

    async with start_server:
        print("WebSocket server started at ws://localhost:8000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())