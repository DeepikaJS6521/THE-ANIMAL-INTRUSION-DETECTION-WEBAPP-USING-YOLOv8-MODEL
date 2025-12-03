# Wild Animal Detection System

## Project Overview

This project implements a real-time wild animal detection system using YOLOv8, presented through a Flask web application. It allows users to log in, view a live webcam feed with animal detections, and access historical data on animal timings and detection patterns.

## Features

*   **Real-time Object Detection:** Detects specified wild animals from a live webcam feed using the YOLOv8 model.
*   **Web Interface:** A user-friendly web application built with Flask, HTML, CSS, and JavaScript.
*   **Secure Login:** Basic authentication to access detection features.
*   **Dynamic Landing Page:** An attractive landing page with information about the project and dynamic effects.
*   **Detection Alerts:** Visual (red alert message) and audio alerts when an animal is detected.
*   **Animal Timing:** A dedicated page displaying the last detection timestamp for each identified animal.
*   **Animal Time Patterns:** A page that analyzes and shows overall and individual animal detection frequency patterns (e.g., most active hours).
*   **Customizable Detection List:** Easily modify which animals the system should detect by updating a list of class IDs in the backend.

## Setup and Installation

Follow these steps to set up and run the project locally.

### Prerequisites

*   Python 3.12.4
*   `pip` (Python package installer)
*   A webcam

### 1. Clone the repository (if applicable) or navigate to your project directory

Make sure your project structure looks like this:

```
D:\New folder\
  animal_detector_web/
    app.py
    requirements.txt
    animaldetection_yolov8.pt
    detect_animals.py (optional, original script)
    static/
      drum.mp3
      wildanimal.png
    templates/
      base.html
      index.html
      login.html
      detect.html
      animal_timing.html
      animal_pattern.html
```

### 2. Install Dependencies

Navigate to the `animal_detector_web` directory in your terminal:

```bash
cd "D:\New folder\animal_detector_web"
pip install -r requirements.txt
```

### 3. Place Your YOLOv8 Model

Ensure your trained YOLOv8 detection model (`animaldetection_yolov8.pt`) is located directly inside the `animal_detector_web` directory, alongside `app.py`.

### 4. Place Audio and Image Files

Ensure `drum.mp3` and `wildanimal.png` are placed in the `animal_detector_web/static/` directory.

## Usage

### 1. Run the Flask Application

From the `animal_detector_web` directory, run the application:

```bash
python app.py
```

### 2. Access the Web Interface

Open your web browser and navigate to `http://127.0.0.1:5000/`.

### 3. Login

Click on the "Get Started" button on the landing page or navigate to `/login`.

*   **Username:** `admin`
*   **Password:** `admin`

### 4. Real-time Detection

After logging in, you will be redirected to the Detection page:

*   The webcam feed will start automatically.
*   Detected animals (lion, leopard, tiger, elephant, hyena, cheetah, bear, horse) will be highlighted with bounding boxes and labels.
*   A red alert message will appear above the camera, and an audio alert will play when an animal is detected.

### 5. View Detection Data

Use the navigation bar at the top to access:

*   **Animal Timing:** Shows a table of all detected animals and their individual detection timestamps.
*   **Animal Pattern:** Displays the most frequent detection times for individual animals and an overall pattern for all animals combined.

## Customizing Detected Animals

To change which animals the system detects, modify the `TARGET_CLASS_IDS` list in `app.py`. Refer to the `CLASS_NAMES` dictionary in `app.py` for a mapping of class IDs to animal names in your model.

## Troubleshooting

### `FileNotFoundError: [Errno 2] No such file or directory: 'animaldetection_yolov8.pt'`

This error occurs if `animaldetection_yolov8.pt` is not in the correct location. Ensure it's directly inside the `animal_detector_web` directory.

### Audio Alert Not Playing

1.  **Browser Autoplay Policy:** Many modern browsers block audio autoplay. You might need to interact with the page (e.g., click anywhere) once to enable audio. Ensure your browser is not muting the tab.
2.  **Developer Console:** Open your browser's developer console (F12) on the Detection page and check the "Console" tab for any errors or warnings related to audio loading or playback (e.g., `Failed to load resource: net::ERR_CONNECTION_REFUSED` or `Uncaught (in promise) DOMException: play() failed because the user didn't interact with the document first.`)
3.  **File Path:** Double-check that `drum.mp3` is correctly placed in `animal_detector_web/static/`.

---

If you encounter any other issues, please provide details, including any error messages from the terminal or browser console.
