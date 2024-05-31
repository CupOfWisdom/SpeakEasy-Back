import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppresses TensorFlow warnings

from keras.models import load_model
from keras.preprocessing.image import img_to_array
import cv2
import numpy as np
import json
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

face_cascade_path = os.path.join(script_dir, 'model_data', 'haarcascade_frontalface_default.xml')
model_path = os.path.join(script_dir, 'model_data', 'model.h5')

# Load the face detection and emotion classification models
face_classifier = cv2.CascadeClassifier(face_cascade_path)
classifier = load_model(model_path)

# Define the emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Ensure correct usage
if len(sys.argv) != 2:
    print("Usage: python process_video.py <video_file_path>")
    sys.exit(1)

video_path = sys.argv[1]
cap = cv2.VideoCapture(video_path)

# Check if video file was opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    sys.exit(1)

# Initialize variables for storing results
emotion_data = []
fps = cap.get(cv2.CAP_PROP_FPS)
emotion_count = {}
emotion_probabilities = {}

print("Processing video.")
# Process each frame of the video
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    labels = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype('float') / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            prediction = classifier.predict(roi)[0]  # Show progress bar
            label = emotion_labels[prediction.argmax()]
            label_position = (x, y)
            cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            label = 'No Faces'
            cv2.putText(frame, label, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Calculate the current time in the video
    current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)

    # Initialize emotion count and probabilities for the current second
    if current_time not in emotion_count:
        emotion_count[current_time] = {emotion: 0 for emotion in emotion_labels}
        emotion_probabilities[current_time] = {emotion: [] for emotion in emotion_labels}

    # Update emotion count and probabilities
    if 'label' in locals():
        emotion_count[current_time][label] += 1
        for i, emo in enumerate(emotion_labels):
            prob = float(prediction[i])
            if np.isnan(prob):
                prob = None
            emotion_probabilities[current_time][emo].append(prob)

# Finalize emotion data for each second
for second in emotion_count:
    prevalent_emotion = max(emotion_count[second], key=emotion_count[second].get)
    average_probabilities = {
        emo: (np.mean(probs) if len(probs) > 0 else None)
        for emo, probs in emotion_probabilities[second].items()
    }
    emotion_data.append({
        "time": second,
        "emotion": prevalent_emotion,
        "probabilities": average_probabilities
    })

# Save emotion data to JSON file
relative_output_path = os.path.join('public', 'json', 'emotion_data.json')
output_path = os.path.join(f'{script_dir}/../api/', relative_output_path)
with open(output_path, 'w') as json_file:
    json.dump(emotion_data, json_file, indent=4)

# Release video capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
