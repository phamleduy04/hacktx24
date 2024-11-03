import cv2
import numpy as np

from base64 import b64encode

import requests

# open image dog.jpg

with open("dog.jpg", "rb") as image_file:
    # turn image file into ndarray
    image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
    
    #convert ndarray to base64 string in format "data:image/jpeg;base64,...."
    base64_img = "data:image/jpeg;base64," + b64encode(cv2.imencode('.jpg', image)[1]).decode()
    
    # print(base64_img)
    
    requests.post("http://localhost:8765/vector/", json={"id": 1, "img": base64_img, "description": "dog"})