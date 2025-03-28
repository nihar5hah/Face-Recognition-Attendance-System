import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import pandas as pd
import time

class AttendanceSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.attendance_file = 'attendance.csv'
        self.images_dir = 'known_faces'
        self.today_attendance = set()
        self.frame_count = 0
        self.fps = 0
        self.last_time = datetime.now()
        
        # Create directory for known faces if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            print(f"Created {self.images_dir} directory")
            
        # Create attendance file if it doesn't exist
        if not os.path.exists(self.attendance_file):
            df = pd.DataFrame(columns=['Name', 'Date', 'Time'])
            df.to_csv(self.attendance_file, index=False)
            print(f"Created {self.attendance_file}")
        
        self.load_known_faces()

    def load_known_faces(self):
        """Load known faces from the images directory"""
        print("\nLoading known faces...")
        loaded = 0
        
        # First, check for files directly in the known_faces directory
        for filename in os.listdir(self.images_dir):
            file_path = os.path.join(self.images_dir, filename)
            if os.path.isfile(file_path) and filename.endswith((".jpg", ".jpeg", ".png")):
                try:
                    # Extract name from filename
                    name = os.path.splitext(filename)[0]
                    if '_' in name and name.split('_')[-1].isdigit():
                        # For files like "john_1.jpg", extract just "john"
                        name = '_'.join(name.split('_')[:-1])
                    
                    self._process_face_image(file_path, name)
                    loaded += 1
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        # Then, check for user directories and their photos
        for dirname in os.listdir(self.images_dir):
            dir_path = os.path.join(self.images_dir, dirname)
            if os.path.isdir(dir_path):
                print(f"Loading photos for {dirname}...")
                user_loaded = 0
                
                # Process all photos in this user's directory
                for filename in os.listdir(dir_path):
                    if filename.endswith((".jpg", ".jpeg", ".png")):
                        try:
                            image_path = os.path.join(dir_path, filename)
                            self._process_face_image(image_path, dirname)
                            user_loaded += 1
                            loaded += 1
                        except Exception as e:
                            print(f"Error loading {dirname}/{filename}: {str(e)}")
                
                print(f"Loaded {user_loaded} photos for {dirname}")
        
        unique_people = len(set(self.known_face_names))
        print(f"\nTotal faces loaded: {loaded}")
        print(f"Total unique people: {unique_people}")
        
        if loaded == 0:
            print("No faces found in known_faces directory!")
            print("Please add some .jpg photos named after the person (e.g., john.jpg)")
            print("Or use the take_multiple_photos.py script to add photos")
    
    def _process_face_image(self, image_path, name):
        """Process a single face image and add it to the known faces"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                print(f"No face found in {image_path}")
                return False
            
            encoding = face_recognition.face_encodings(image, face_locations)[0]
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            print(f"Loaded: {name} from {os.path.basename(image_path)}")
            return True
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return False

    def mark_attendance(self, name):
        """Mark attendance for a recognized face"""
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        time_string = now.strftime('%H:%M:%S')
        
        df = pd.read_csv(self.attendance_file)
        
        # Check if attendance already marked for today
        if not ((df['Name'] == name) & (df['Date'] == date_string)).any():
            new_row = {'Name': name, 'Date': date_string, 'Time': time_string}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.attendance_file, index=False)
            print(f"\nMarked attendance for {name} at {time_string}")
            self.today_attendance.add(name)

    def draw_dashboard(self, frame):
        """Draw status dashboard on the frame"""
        height, width = frame.shape[:2]
        
        # Calculate FPS
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            current_time = datetime.now()
            time_diff = (current_time - self.last_time).total_seconds()
            self.fps = 30 / time_diff if time_diff > 0 else 0
            self.last_time = current_time

        # Draw semi-transparent overlay for dashboard
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 100), (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw dashboard content
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Title and time
        cv2.putText(frame, "Face Recognition Attendance System", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Date: {date_str} | Time: {time_str}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Status information
        status_text = f"FPS: {self.fps:.1f} | Registered: {len(set(self.known_face_names))} | Present Today: {len(self.today_attendance)}"
        cv2.putText(frame, status_text, (width - 400, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Controls
        controls_text = "Controls: Q - Quit | R - Reset Daily Attendance"
        cv2.putText(frame, controls_text, (width - 400, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    def draw_face_box(self, frame, face_location, name):
        """Draw face detection box and name label"""
        top, right, bottom, left = face_location
        
        # Draw face box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Draw name label with background
        label_bg = frame.copy()
        cv2.rectangle(label_bg, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
        cv2.addWeighted(label_bg, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                   cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    def start_recognition(self):
        """Start the face recognition system"""
        print("\nStarting face recognition system...")
        print("Controls:")
        print("- Press 'q' to quit")
        print("- Press 'r' to reset daily attendance")
        
        # Initialize the webcam with multiple attempts
        cap = None
        for attempt in range(3):
            print(f"Attempting to open webcam (attempt {attempt+1}/3)...")
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Try DirectShow backend
            if cap.isOpened():
                print("Webcam opened successfully!")
                break
            time.sleep(1)
        
        if not cap or not cap.isOpened():
            print("Error: Could not open webcam after multiple attempts!")
            print("Please check if your webcam is connected and not in use by another application.")
            return
            
        # Wait a moment for the camera to initialize
        time.sleep(1)
        
        print("\nWebcam started successfully!")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame, retrying...")
                time.sleep(0.5)
                continue

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find faces in the frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Draw dashboard
            self.draw_dashboard(frame)

            # Process each face
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    self.mark_attendance(name)

                # Draw face box and label
                self.draw_face_box(frame, [coord * 4 for coord in face_location], name)

            cv2.imshow('Face Recognition Attendance System', frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nShutting down...")
                break
            elif key == ord('r'):
                self.today_attendance.clear()
                print("\nDaily attendance reset!")

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("=== Face Recognition Attendance System ===\n")
    system = AttendanceSystem()
    system.start_recognition()
