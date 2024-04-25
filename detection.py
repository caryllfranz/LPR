import requests
import subprocess
import cv2
import yolov5
import os
import time

processed_plates = set()


model = yolov5.load("keremberke/yolov5n-license-plate")


model.conf = 0.8
model.iou = 0.8
model.agnostic = False
model.multi_label = False
model.max_det = 1000


cap = cv2.VideoCapture(1)

last_time = time.time()

while True:

    ret, frame = cap.read()

    results = model(frame, size=640)

    predictions = results.pred[0]
    boxes = predictions[:, :4]
    scores = predictions[:, 4]
    categories = predictions[:, 5]

    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), thickness=2)

        license_plate = frame[y1:y2, x1:x2]
        file_path = "licenseplate.png"
        cv2.imwrite(file_path, license_plate)

        # Convert license plate bytes to a hash for storage and checking
        license_plate_hash = hash(license_plate.tobytes())

        if license_plate_hash in processed_plates:
            continue

        # Add the license plate hash to the set of processed plates
        processed_plates.add(license_plate_hash)

        if time.time() - last_time >= 2:
            last_time = time.time()

            if license_plate.tobytes() in processed_plates:
                continue

            command = "python plate_recognition.py -a 59db79c4062b1ed23fbe9ef9e26c20b16664028c licenseplate.png"
            output = subprocess.run(command, shell=True, capture_output=True, text=True)

            file_name = "plate.txt"
            if os.path.exists(file_name):
                with open(file_name, "r") as file:
                    plate_value = file.read().strip()
                    print(plate_value)

            if plate_value is not None and plate_value != "":
                if plate_value in processed_plates:
                    continue

                url = "http://kapark.pythonanywhere.com/update_detection"
                params = {"plate": plate_value}
                try:
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        slot = data.get("slot")
                        reserved_area = ""
                        if slot:
                            slot = int(slot)
                            if 1 <= slot <= 8:
                                reserved_area = "A"
                            elif 9 <= slot <= 16:
                                reserved_area = "B"
                            elif 17 <= slot <= 24:
                                reserved_area = "C"
                            print(f"You are reserved in area {reserved_area}")

                    elif response.status_code == 404:
                        url = "http://kapark.pythonanywhere.com/write_license"
                        params = {"plate": plate_value}
                        try:
                            response = requests.get(url, params=params)
                            if response.status_code == 200:
                                print("Plate not reserved.")
                                processed_plates.add(plate_value)
                            else:
                                print("Error:", response.text)
                        except requests.exceptions.RequestException as e:
                            print("Error making request:", e)

                    else:
                        print("Error:", response.text)
                except requests.exceptions.RequestException as e:
                    print("Error making request:", e)

            processed_plates.add(license_plate.tobytes())

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
