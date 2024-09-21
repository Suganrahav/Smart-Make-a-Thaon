import csv
import cv2
import numpy as np
import time
import sys

weights_path = r"C:\\Users\\welcome\\Downloads\\yolov3.weights"
cfg_path = r"C:\\Users\\welcome\\Downloads\\yolov3.cfg"
coco_names_path = r"C:\\Users\\welcome\\Downloads\\coco.names.txt"

net = cv2.dnn.readNet(weights_path, cfg_path)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

try:
    with open(coco_names_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]
except IOError:
    print(f"Error: Could not read class names from {coco_names_path}")
    sys.exit()


# Function to check for High/Medium priority in emergency.csv
def check_emergency_priority():
    try:
        with open('emergency.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] in ['High', 'Medium']:  # Checking for High or Medium priority
                    return True
    except FileNotFoundError:
        print("emergency.csv not found.")
    return False


def detect_objects(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    class_ids = []
    confidences = []
    boxes = []
    
    car_count = 0
    truck_count = 0
    
    for out in outs:
        for detection in out:
            if len(detection) >= 85:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3 and classes[class_id] in ['car', 'truck']:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
    
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.4)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            if label == 'car':
                car_count += 1
            elif label == 'truck':
                truck_count += 1
    
    return car_count, truck_count


def process_video(video_path, duration):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return 0, 0

    total_car_count = 0
    total_truck_count = 0
    frame_count = 0

    start_time = time.time()

    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', 1920, 1080)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        car_count, truck_count = detect_objects(frame)
        total_car_count += car_count
        total_truck_count += truck_count
        frame_count += 1

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        elapsed_time = time.time() - start_time
        if elapsed_time > duration:
            break

    cap.release()
    cv2.destroyAllWindows()

    avg_car_count = total_car_count // frame_count if frame_count > 0 else 0
    avg_truck_count = total_truck_count // frame_count if frame_count > 0 else 0

    return avg_car_count, avg_truck_count


def calculate_duration():
    avg_car_count1, avg_truck_count1 = process_video(video_path1, 5)
    avg_car_count2, avg_truck_count2 = process_video(video_path2, 5)

    combined_count_video1 = avg_car_count1 + avg_truck_count1
    combined_count_video2 = avg_car_count2 + avg_truck_count2

    rate = 1.5
    duration_per_vehicle1 = rate * combined_count_video1 if combined_count_video1 > 0 else 5
    duration_per_vehicle2 = rate * combined_count_video2 if combined_count_video2 > 0 else 5

    return duration_per_vehicle1, duration_per_vehicle2


# Modified control_signals function
def control_signals():
    while True:
        # Check if there's an emergency every second
        if check_emergency_priority():
            print("Emergency detected: Signal 1 is GREEN for 60 seconds")
            countdown(60)  # Signal 1 stays green for 60 seconds in case of High or Medium priority
        else:
            # Regular signal logic
            duration_per_vehicle1, duration_per_vehicle2 = calculate_duration()
            print(f"Signal 1 is GREEN for {duration_per_vehicle1:.2f} seconds")
            countdown(duration_per_vehicle1)

            print("Signal 1 is now RED. Switching to Signal 2.")
            print(f"Signal 2 is GREEN for {duration_per_vehicle2:.2f} seconds")
            countdown(duration_per_vehicle2)

            print("Signal 2 is now RED. Switching back to Signal 1.")
        
        time.sleep(1)  # Wait for 1 second before checking emergency.csv again


def countdown(duration):
    for remaining_time in range(int(duration), 0, -1):
        sys.stdout.write(f"\rTime left: {remaining_time} seconds")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")


# Video paths (for testing purposes)
video_path1 = "C:\\Users\\welcome\\Downloads\\3206967-uhd_3840_2160_30fps.mp4"
video_path2 = "C:\\Users\\welcome\\Downloads\\19696722-hd_1080_1920_30fps.mp4"


if __name__ == "__main__":
    control_signals()
