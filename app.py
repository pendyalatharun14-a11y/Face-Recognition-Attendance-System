
import cv2
import os
import csv
import numpy as np
from datetime import datetime

# Face Recognition Attendance System

DATASET_PATH = "known_faces"
ATTENDANCE_FILE = "attendance.csv"

# Load OpenCV face detector
face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Create attendance file if it doesn't exist
if not os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Date", "Time"])

# Train face recognition model
recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []
names = {}

label_id = 0

for person in os.listdir(DATASET_PATH):
    person_path = os.path.join(DATASET_PATH, person)

    if not os.path.isdir(person_path):
        continue

    names[label_id] = person

    for image_name in os.listdir(person_path):
        image_path = os.path.join(person_path, image_name)

        image = cv2.imread(image_path)

        if image is None:
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detected = face_detector.detectMultiScale(
            gray, 1.3, 5
        )

        if len(detected) == 0:
            continue

        x, y, w, h = max(
            detected, key=lambda box: box[2] * box[3]
        )

        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        faces.append(face)
        labels.append(label_id)

    label_id += 1

if len(faces) == 0:
    print("No face images found in known_faces folder.")
    print("Add student photos before running the program.")
    raise SystemExit

recognizer.train(
    faces, np.array(labels, dtype=np.int32)
)

print("Face Recognition Model Trained Successfully!")

marked_today = set()

if os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("Date") == datetime.now().strftime("%Y-%m-%d"):
                marked_today.add(row.get("Name"))

# Start webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot access webcam.")
    raise SystemExit

print("Attendance System Started!")
print("Press Q to exit.")

while True:
    success, frame = camera.read()

    if not success:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detected_faces = face_detector.detectMultiScale(
        gray, 1.3, 5
    )

    for (x, y, w, h) in detected_faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        label, confidence = recognizer.predict(face)

        if confidence < 70 and label in names:
            name = names[label]

            color = (0, 255, 0)

            if name not in marked_today:
                now = datetime.now()

                with open(
                    ATTENDANCE_FILE, "a", newline=""
                ) as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        name,
                        now.strftime("%Y-%m-%d"),
                        now.strftime("%H:%M:%S")
                    ])

                marked_today.add(name)
                print(name, "Attendance Marked!")

        else:
            name = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(
            frame, (x, y), (x+w, y+h), color, 2
        )

        cv2.putText(
            frame, name, (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8, color, 2
        )

    cv2.imshow(
        "Face Recognition Attendance System", frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
