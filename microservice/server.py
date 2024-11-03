from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from image_processor import process_image

app = FastAPI()

@app.post("/process_image/")
async def process_uploaded_image(file: UploadFile = File(...)):
    # Read the image file
    image = await file.read()
    nparr = np.frombuffer(image, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Process the image
    box_data = process_image(frame)

    return JSONResponse(content=box_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Server started at http://localhost:8000")