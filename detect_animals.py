from ultralytics import YOLO
from playsound import playsound

# Load a custom trained model
model = YOLO('animaldetection_yolov8.pt')  # Ensure this path is correct relative to where the script is run

# Run webcam detection
# The 'stream=True' argument allows for iterating through the results as they come in
results = model.predict(source='0', show=True, classes=[21, 20, 40, 7, 24, 17, 2, 1, 15], stream=True)

for r in results:
    if len(r.boxes) > 0: # Check if any objects are detected in the current frame
        playsound('D:\\New folder\\drum.mp3')
