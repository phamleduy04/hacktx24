import cv2
import asyncio
import websockets
import numpy as np
import base64

async def send_video(websocket,path):
    
  cam = cv2.VideoCapture(0)

  x,y,w,h=100,100,200,150  #hardcoded for now
  dx,dy=5,3
  dw,dh=3,5

  while True:
        success, frame = cam.read()
        if not success:
            break
        
        x += dx
        y += dy
        w+=dw
        h+=dh
        if w>215 or w<185:
            dw=-dw
        if h>175 or h<125:
            dh=-dh
        # Check for boundaries and reverse direction if hitting the edge
        if x + w > frame.shape[1] or x < 0:
            dx = -dx
        if y + h > frame.shape[0] or y < 0:
            dy = -dy
        
        color = (0, 255, 0) #green
        thickness = 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
       

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = base64.b64encode(buffer).decode('utf-8')

        # Sending frames to the WebSocket client
        await websocket.send(frame)

  cam.release()


start_server=websockets.serve(send_video,'localhost',8000)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started at ws://localhost:8000")
asyncio.get_event_loop().run_forever()
