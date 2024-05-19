
import cv2
import mediapipe as mp
import numpy as np
import json

# Function to simulate emotion detection (replace with your actual emotion detection logic)
def detect_emotions(frame):
    # Your emotion detection code here
    # This is just a placeholder for illustration purposes
    emotions = ["happy", "sad", "neutral"]
    probabilities = np.random.dirichlet(np.ones(len(emotions)), size=1)[0]
    detected_emotion = emotions[np.argmax(probabilities)]
    return detected_emotion, dict(zip(emotions, probabilities))

# Path to your video file
video_path = '../data/videos/video.mp4'

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# List to store emotion data
emotion_data = []

# Frame rate of the video
fps = cap.get(cv2.CAP_PROP_FPS)

# Initialize a dictionary to store emotion count and probabilities per second
emotion_count = {}
emotion_probabilities = {}

while True:
    # Read a frame from the video
    ret, frame = cap.read()

    # If frame reading was not successful, break the loop
    if not ret:
        break

    # Detect emotions on the frame
    emotion, probabilities = detect_emotions(frame)

    # Calculate the current time in the video
    current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)

    # Append the emotion and timestamp to the emotion_data list
    if current_time not in emotion_count:
        emotion_count[current_time] = {"happy": 0, "sad": 0, "neutral": 0}
        emotion_probabilities[current_time] = {"happy": [], "sad": [], "neutral": []}

    emotion_count[current_time][emotion] += 1

    for emo, prob in probabilities.items():
        emotion_probabilities[current_time][emo].append(prob)

    # Display the emotion and probabilities on the frame (or any other feedback mechanism)
    cv2.putText(frame, f'Emotion: {emotion}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    y_offset = 60
    for emo, prob in probabilities.items():
        cv2.putText(frame, f'{emo}: {prob:.2f}', (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
        y_offset += 30

    # Show the frame
    cv2.imshow('Video', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close display windows
cap.release()
cv2.destroyAllWindows()

# Determine the prevalent emotion for each second and store probabilities
for second in emotion_count:
    prevalent_emotion = max(emotion_count[second], key=emotion_count[second].get)
    average_probabilities = {emo: np.mean(probs) for emo, probs in emotion_probabilities[second].items()}
    emotion_data.append({
        "time": second,
        "emotion": prevalent_emotion,
        "probabilities": average_probabilities
    })

# Write the emotion data to a JSON file
with open('../data/json/emotion_data.json', 'w') as json_file:
    json.dump(emotion_data, json_file, indent=4)

