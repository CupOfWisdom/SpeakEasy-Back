# Assume this is your updated Python script, save it as process_video.py
import sys
import cv2
import mediapipe as mp
import numpy as np
import json
import os

def detect_emotions(frame):
    # Your emotion detection code here
    emotions = ["happy", "sad", "neutral"]
    probabilities = np.random.dirichlet(np.ones(len(emotions)), size=1)[0]
    detected_emotion = emotions[np.argmax(probabilities)]
    return detected_emotion, dict(zip(emotions, probabilities))

if len(sys.argv) != 2:
    print("Usage: python process_video.py <video_file_path>")
    sys.exit(1)

video_path = sys.argv[1]
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    sys.exit(1)

emotion_data = []
fps = cap.get(cv2.CAP_PROP_FPS)
emotion_count = {}
emotion_probabilities = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    emotion, probabilities = detect_emotions(frame)
    current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)

    if current_time not in emotion_count:
        emotion_count[current_time] = {"happy": 0, "sad": 0, "neutral": 0}
        emotion_probabilities[current_time] = {"happy": [], "sad": [], "neutral": []}

    emotion_count[current_time][emotion] += 1
    for emo, prob in probabilities.items():
        emotion_probabilities[current_time][emo].append(prob)

for second in emotion_count:
    prevalent_emotion = max(emotion_count[second], key=emotion_count[second].get)
    average_probabilities = {emo: np.mean(probs) for emo, probs in emotion_probabilities[second].items()}
    emotion_data.append({
        "time": second,
        "emotion": prevalent_emotion,
        "probabilities": average_probabilities
    })

output_path = os.path.join(os.path.dirname(video_path), 'emotion_data.json')
with open(output_path, 'w') as json_file:
    json.dump(emotion_data, json_file, indent=4)
