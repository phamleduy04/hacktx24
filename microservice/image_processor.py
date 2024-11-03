import numpy as np
import supervision as sv
from ultralytics import YOLO

# Load the models
detect_model = YOLO("yolo11s.pt")
clothes_model = YOLO("clothes.pt")

tracker = sv.ByteTrack()
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

def detect_clothes(cropped_frame: np.ndarray) -> np.ndarray:
    res = clothes_model(cropped_frame)[0]
    detections = sv.Detections.from_ultralytics(res)
    if len(detections.data['class_name']) >= 2:
        return detections.data['class_name']
    else:
        return None

def process_image(frame: np.ndarray):
    detect_res = detect_model(frame)[0]
    detections = sv.Detections.from_ultralytics(detect_res)
    detections = detections[detections.class_id == 0]
    detections = tracker.update_with_detections(detections)

    clothes = {}
    # Crop the detected images and save
    for xyxy, mask, confidence, class_id, tracker_id, data in detections:
        # Segment each of the cropped image
        cropped_img = sv.crop_image(image=frame, xyxy=xyxy)
        
        clothes[tracker_id] = detect_clothes(cropped_img)

    labels = [
        f"#{tracker_id} {detect_res.names[class_id]} {clothes[tracker_id]}"
        for class_id, tracker_id
        in zip(detections.class_id, detections.tracker_id)
    ]

    annotated_frame = box_annotator.annotate(
        frame.copy(), detections=detections)
    
    annotated_frame = label_annotator.annotate(
        annotated_frame, detections=detections, labels=labels)

    # Extract bounding box data
    box_data = []
    for xyxy, mask, confidence, class_id, tracker_id, data in detections:
        print(xyxy)
        box_data.append({
            "tracker_id": int(tracker_id),
            "class_id": int(class_id),
            "confidence": float(confidence),
            "xyxy": xyxy.tolist(),
            "clothes": clothes[tracker_id].tolist() if clothes[tracker_id] is not None else []
        })

    return box_data