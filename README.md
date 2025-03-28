# Face Recognition Attendance System

A Python-based attendance system using OpenCV and face_recognition library that automatically records attendance when it recognizes faces.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Add known faces:
   - Create photos of people you want to recognize
   - Save them in the `known_faces` directory
   - Name the files with the person's name (e.g., `john_doe.jpg`)
   - Make sure each image has exactly one clear face

## Usage

1. Run the attendance system:
```bash
python attendance_system.py
```

2. The system will:
   - Open your webcam
   - Recognize faces in real-time
   - Mark attendance in `attendance.csv`
   - Display names of recognized people
   
3. Press 'q' to quit the application

## Features

- Real-time face detection and recognition
- Automatic attendance marking with timestamp
- Prevents duplicate attendance entries for the same day
- CSV-based attendance record keeping
