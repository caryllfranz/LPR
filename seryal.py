import requests
import subprocess
import cv2
import yolov5
import serial
import torch
import os
import time

# Load model
model = yolov5.load("keremberke/yolov5n-license-plate")

ser = serial.Serial(' /dev/ttyACM0', baudrate=9600, timeout=1)

# Set model parameters
model.conf = 0.25  # NMS confidence threshold
model.iou = 0.45  # NMS IoU threshold
model.agnostic = False  # NMS class-agnostic
model.multi_label = False  # NMS multiple labels per box
model.max_det = 1000  # Maximum number of detections per image

# Open webcam
cap = cv2.VideoCapture(
    0
)  # Use 0 for the default webcam, or change to the appropriate index for other webcams

last_time = time.time()  # Initialize last_time

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Perform inference
    results = model(frame, size=640)

    # Parse results
    predictions = results.pred[0]
    boxes = predictions[:, :4]  # x1, y1, x2, y2
    scores = predictions[:, 4]
    categories = predictions[:, 5]

    # Draw bounding boxes on the frame
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness=2)

        license_plate = frame[y1:y2, x1:x2]
        file_path = "licenseplate.png"  # Use a fixed file name
        cv2.imwrite(file_path, license_plate)
        # print(
        #     "The path of licenseplate.png is:", os.path.abspath(file_path)
        # )  # Print file path

        # Check if 3 seconds have passed since the last command execution
        if time.time() - last_time >= 2:
            command = "python plate_recognition.py -a 59db79c4062b1ed23fbe9ef9e26c20b16664028c licenseplate.png"
            output = subprocess.run(command, shell=True, capture_output=True, text=True)
            last_time = time.time()  # Update last_time
    
            file_name = "plate.txt"
            if os.path.exists(file_name):
                with open(file_name, "r") as file:
                    plate_value = file.read().strip()
                print(plate_value)

            
            if plate_value:
                url = "http://kapark.pythonanywhere.com//update_detection"
                params = {"plate": plate_value}
                try:
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        print("Plate Found int Database.")
                        ser.write(b'B')
                    elif response.status_code == 404:
                        print("Plate not found in the database.")
                        ser.write(b'A')
                    else:
                        print("Error:", response.text)
                except requests.exceptions.RequestException as e:
                    print("Error making request:", e)

            processed_plates = set()

            if plate_value not in processed_plates:
                url = "http://kapark.pythonanywhere.com/write_license"
                params = {"plate": plate_value}
                try:
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        print("Plate detection inserted.")
                        # Add the processed plate to the set
                        processed_plates.add(plate_value)
                    elif response.status_code == 404:
                        print("Plate not found in the database.")
                    else:
                        print("Error:", response.text)
                except requests.exceptions.RequestException as e:
                    print("Error making request:", e)

    # Display the frame
    cv2.imshow("Webcam", frame)

    # Check for 'q' key press to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
