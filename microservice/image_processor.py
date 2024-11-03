import cv2
import webcolors
import numpy as np
import supervision as sv
from ultralytics import YOLO
from dominant_color import DominantColor

detect_model = YOLO("yolo11s.pt")
clothes_model = YOLO("best.pt")

tracker = sv.ByteTrack()
box_annotator = sv.BoxAnnotator()
mask_annotator = sv.MaskAnnotator()
label_annotator = sv.LabelAnnotator()

def closest_color(requested_color):
    min_distance = float('inf')
    closest_name = None

    # Iterate through all known colors in webcolors
    for hex_code, color_name in webcolors._definitions._CSS3_HEX_TO_NAMES.items():
        r, g, b = webcolors.hex_to_rgb(hex_code)
        
        # Calculate Euclidean distance
        distance = ((r - requested_color[0]) ** 2 +
                    (g - requested_color[1]) ** 2 +
                    (b - requested_color[2]) ** 2) ** 0.5

        # Update the closest name if this color is closer
        if distance < min_distance:
            min_distance = distance
            closest_name = color_name

    return closest_name

def classify_color(cropped_frame):
    # Calculate the dominant color
    dominant_color = DominantColor(cropped_frame)

    print(dominant_color.rgb)
    
    # Find the closest named color
    closest_name = closest_color(dominant_color.rgb)
    
    return closest_name

# Example usage:
# res_color = classify_color(cropped_frame)
# print("Closest named color:", res_color)
    

def mid_split_top_bottom(cropped_frame: np.ndarray):
    # Get the height of the frame
    height = cropped_frame.shape[0]
    
    # Calculate the midpoint
    midpoint = height // 2
    
    # Split the frame into top and bottom halves
    top_cropped_frame = cropped_frame[:midpoint, :]
    bottom_cropped_frame = cropped_frame[midpoint:, :]

    return f"{classify_color(top_cropped_frame)} unknown top, and {classify_color(bottom_cropped_frame)} unknown bottom."
    

def detect_clothes(cropped_frame: np.ndarray) -> np.ndarray:
    res = clothes_model(cropped_frame)[0]
    detections = sv.Detections.from_ultralytics(res)
    if len(detections.data['class_name']) >= 1:
        clothes_str = ""
        for xyxy, mask, confidence, class_id, tracker_id, data in detections:
            print(confidence)
            # Convert mask to uint8 if it is boolean
            mask_uint8 = mask.astype(np.uint8) * 255

            # Find contours of the solid mask annotation
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get the bounding box of the largest contour
                x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                
                # Center of the bounding box
                center_x, center_y = x + w // 2, y + h // 2

                # Reduce bounding box dimensions by half
                reduced_side_length = max(w, h) // 2
                half_reduced_side = reduced_side_length // 2

                # Calculate the smaller square crop coordinates
                square_x1 = max(center_x - half_reduced_side, 0)
                square_y1 = max(center_y - half_reduced_side, 0)
                square_x2 = min(center_x + half_reduced_side, cropped_frame.shape[1])
                square_y2 = min(center_y + half_reduced_side, cropped_frame.shape[0])

                # Crop the image to this smaller square region
                cropped_img = cropped_frame[square_y1:square_y2, square_x1:square_x2]

                with sv.ImageSink(target_dir_path="resu2lt") as sink:
                    sink.save_image(image=cropped_img)

                
            clothes_str += f"{classify_color(cropped_img)} {data['class_name']}, "

            
        return clothes_str
    else:
        return mid_split_top_bottom(cropped_frame)

def detect_and_track_people(frame: np.ndarray) -> np.ndarray:
    detect_res = detect_model(frame)[0]
    detections = sv.Detections.from_ultralytics(detect_res)
    detections = detections[detections.class_id == 0]
    detections = detections[detections.confidence > 0.5]
    detections = tracker.update_with_detections(detections)

    clothes = {}
    #Crop the detected images and save
    for xyxy, mask, confidence, class_id, tracker_id, data in detections:
        
        #Segment each of the cropped image
        cropped_img = sv.crop_image(image=frame, xyxy=xyxy)
        clothes[tracker_id] = detect_clothes(cropped_img)


    labels = [
        f"{detect_res.names[class_id]} #{tracker_id} {clothes[tracker_id]}"
        for class_id, tracker_id
        in zip(detections.class_id, detections.tracker_id)
    ]

    print(labels, detections.xyxy)

    annotated_frame = box_annotator.annotate(
        frame.copy(), detections=detections)
    
    annotated_frame = label_annotator.annotate(
        annotated_frame, detections=detections, labels=labels)

    # Extract bounding box data
    box_data = []
    image_height, image_width = frame.shape[:2]
    for xyxy, mask, confidence, class_id, tracker_id, data in detections:
        x1, y1, x2, y2 = xyxy
        normalized_xyxy = [x1 / image_width, y1 / image_height, x2 / image_width, y2 / image_height]
        normalized_xyxy = [float(coord) for coord in normalized_xyxy]  # Convert coordinates to standard floats

        box_data.append({
            "tracker_id": int(tracker_id),
            "class_id": int(class_id),
            "confidence": float(confidence),
            "xyxy": normalized_xyxy,
            "clothes": clothes[tracker_id]
        })

    return box_data

def get_json_result(frame: np.ndarray):
    detect_res = detect_model(frame)[0]
    detections = sv.Detections.from_ultralytics(detect_res)
    detections = detections[detections.class_id == 0]
    detections = detections[detections.confidence > 0.5]
    detections = tracker.update_with_detections(detections)

    clothes = {}
    normalized_coords = {}
    #Crop the detected images and save
    for xyxy, mask, confidence, class_id, tracker_id, data in detections:
        #Segment each of the cropped image
        cropped_img = sv.crop_image(image=frame, xyxy=xyxy)
        
        clothes[tracker_id] = detect_clothes(cropped_img)
        coords = [ x_y / frame.shape[i % 2 == 0] for i, x_y in enumerate(xyxy)]
        normalized_coords[tracker_id] = coords   
    
    result = []
    for class_id, tracker_id in zip(detections.class_id, detections.tracker_id):
        text = f"{detect_res.names[class_id]} #{tracker_id} {clothes[tracker_id]}"
        xyxy = [float(coord) for coord in normalized_coords[tracker_id]]  # Convert coordinates to standard floats

        result.append({
            "tracker_id": int(tracker_id),
            "text": text,
            "xyxy": xyxy
        })

    return result

def pre_process_frame(frame: np.ndarray):
    #Make it brighter
    frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=0)
    return frame
