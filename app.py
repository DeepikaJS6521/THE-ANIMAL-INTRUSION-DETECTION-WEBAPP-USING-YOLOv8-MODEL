import cv2
import os
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response, session, jsonify
from ultralytics import YOLO

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a strong, random key in production

# Load the YOLOv8 model
model = YOLO('animaldetection_yolov8.pt')

# Map class IDs to animal names
CLASS_NAMES = {
    21: 'lion', 20: 'leopard', 40: 'tiger', 7: 'elephant', 17: 'hyena', 2: 'cheetah', 1: 'bear', 15: 'horse'
}

# Define the classes we want to detect (using the IDs previously identified)
TARGET_CLASS_IDS = [21, 20, 40, 7, 17, 2, 1, 15] # lion, leopard, tiger, elephant, hyena, cheetah, bear, horse

# Global variables to control the video stream and detection status
video_stream_active = False
animal_detected_flag = False
latest_detected_animals = []
last_detection_time = None
detection_history = {} # Stores {animal_name: [timestamp1, timestamp2, ...]}
overall_detection_timestamps = [] # Stores all detection timestamps across all animals
selected_animal_filter = 'all' # New global variable to store the selected animal
selected_sound_file = 'drum.mp3' # New global variable to store the selected sound file

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':  # Simple authentication
            session['logged_in'] = True
            return redirect(url_for('detect'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/detect')
def detect():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('detect.html', selected_animal=selected_animal_filter, selected_sound=selected_sound_file)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    global video_stream_active, animal_detected_flag, detection_history, latest_detected_animals, overall_detection_timestamps
    video_stream_active = False
    animal_detected_flag = False
    detection_history = {} # Clear history on logout
    latest_detected_animals = [] # Clear latest detected animals
    overall_detection_timestamps = [] # Clear overall detection timestamps
    return redirect(url_for('index'))

@app.route('/select_animal', methods=['POST'])
def select_animal():
    global selected_animal_filter
    selected_animal_filter = request.form.get('selected_animal', 'all')
    print(f"Selected animal for detection: {selected_animal_filter}")
    return redirect(url_for('detect'))

@app.route('/select_sound', methods=['POST'])
def select_sound():
    global selected_sound_file
    selected_sound_file = request.form.get('selected_sound', 'drum.mp3')
    print(f"Selected sound file: {selected_sound_file}")
    return redirect(url_for('detect'))

# --- Video Streaming Logic ---

def generate_frames():
    global video_stream_active, animal_detected_flag, detection_history, latest_detected_animals, overall_detection_timestamps, selected_animal_filter
    camera = cv2.VideoCapture(0)  # Use 0 for default webcam
    if not camera.isOpened():
        print("Error: Could not open camera.")
        return

    video_stream_active = True
    while video_stream_active:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Perform detection
            # If a specific animal is selected, filter the target classes
            if selected_animal_filter != 'all':
                filtered_class_ids = [k for k, v in CLASS_NAMES.items() if v == selected_animal_filter]
            else:
                filtered_class_ids = TARGET_CLASS_IDS
            
            results = model.predict(source=frame, classes=filtered_class_ids, verbose=False)
            
            detected_animals_in_frame = set() # Use a set to store unique animal names in current frame

            # Check for detections and set flag
            detected_in_frame = False
            current_frame_time = datetime.now() # Get timestamp for the current frame

            for r in results:
                if len(r.boxes) > 0:
                    detected_in_frame = True
                    for box in r.boxes:
                        class_id = int(box.cls[0])
                        animal_name = CLASS_NAMES.get(class_id)
                        if animal_name and (selected_animal_filter == 'all' or animal_name == selected_animal_filter):
                            detected_animals_in_frame.add(animal_name)
                            if animal_name not in detection_history:
                                detection_history[animal_name] = []
                            detection_history[animal_name].append(current_frame_time) # Append timestamp for individual animal
            
            if detected_in_frame:
                animal_detected_flag = True
                latest_detected_animals = list(detected_animals_in_frame)
                overall_detection_timestamps.append(current_frame_time) # Append to overall timestamps
            else:
                latest_detected_animals = []

            # Iterate through results to draw bounding boxes and labels
            for r in results:
                im_array = r.plot()  # plot returns an RGB numpy array
                frame = im_array # Use the RGB array directly

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\n'
                   b'Content-Type: image/jpeg\n\n' + frame + b'\n')

    camera.release()
    print("Camera released.")

@app.route('/video_feed')
def video_feed():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_status')
def detection_status():
    global animal_detected_flag, latest_detected_animals
    
    response_data = {
        'detected': animal_detected_flag,
        'latest_detection': latest_detected_animals
    }

    # Reset the flag and latest detections after checking
    animal_detected_flag = False  
    latest_detected_animals = []

    return jsonify(response_data)

@app.route('/animal_timing')
def animal_timing():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Format detection history for display
    formatted_timings = {animal: [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in timestamps] 
                         for animal, timestamps in detection_history.items()}
    return render_template('animal_timing.html', animal_timings=formatted_timings)

@app.route('/animal_pattern')
def animal_pattern():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    pattern_data = {}
    # Individual animal patterns
    for animal, timestamps in detection_history.items():
        if timestamps:
            hourly_counts = {hour: 0 for hour in range(24)}
            for ts in timestamps:
                hourly_counts[ts.hour] += 1
            
            max_count = 0
            most_frequent_hours = []
            for hour, count in hourly_counts.items():
                if count > max_count:
                    max_count = count
                    most_frequent_hours = [f"{hour}:00-{hour+1}:00"]
                elif count == max_count and count > 0:
                    most_frequent_hours.append(f"{hour}:00-{hour+1}:00")
            
            if most_frequent_hours:
                pattern_data[animal] = f"Most active during: {', '.join(most_frequent_hours)} (with {max_count} detections)"
            else:
                pattern_data[animal] = "Not enough data for pattern analysis."
        else:
            pattern_data[animal] = "No detections recorded."

    # Overall animal pattern
    overall_pattern_info = "No overall pattern available yet. Continue detection to gather data."
    if overall_detection_timestamps:
        overall_hourly_counts = {hour: 0 for hour in range(24)}
        for ts in overall_detection_timestamps:
            overall_hourly_counts[ts.hour] += 1
        
        overall_max_count = 0
        overall_most_frequent_hours = []
        for hour, count in overall_hourly_counts.items():
            if count > overall_max_count:
                overall_max_count = count
                overall_most_frequent_hours = [f"{hour}:00-{hour+1}:00"]
            elif count == overall_max_count and count > 0:
                overall_most_frequent_hours.append(f"{hour}:00-{hour+1}:00")

        if overall_most_frequent_hours:
            overall_pattern_info = f"Overall most active during: {', '.join(overall_most_frequent_hours)} (with {overall_max_count} total detections)"
        
    return render_template('animal_pattern.html', animal_patterns=pattern_data, overall_pattern=overall_pattern_info)

@app.route('/stop_video_feed', methods=['POST'])
def stop_video_feed():
    global video_stream_active, animal_detected_flag, latest_detected_animals, last_detection_time, detection_history
    video_stream_active = False
    animal_detected_flag = False
    latest_detected_animals = []
    last_detection_time = None
    detection_history = {} # Clear detection history on stop
    latest_detected_animals = [] # Clear latest detected animals
    session.pop('logged_in', None) # Log out user
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the templates directory exists
    if not os.path.exists(os.path.join(app.root_path, 'templates')):
        os.makedirs(os.path.join(app.root_path, 'templates'))
    app.run(debug=True)
