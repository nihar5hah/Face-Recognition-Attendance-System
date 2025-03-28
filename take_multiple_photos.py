import cv2
import os
import sys
import time
import numpy as np

def take_multiple_photos(name, num_photos=3, delay=2):
    """
    Take multiple photos of the same person to improve recognition accuracy
    
    Args:
        name: Person's name
        num_photos: Number of photos to take
        delay: Delay between photos in seconds
    """
    print(f"\nTaking {num_photos} photos for {name}")
    print("Position the person in front of the camera")
    print("Photos will be taken automatically with a delay")
    print("Press Q at any time to quit")
    
    # Create directory for this person if it doesn't exist
    user_dir = os.path.join('known_faces', name)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        print(f"Created directory for {name}: {user_dir}")
    
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
        return False
    
    # Wait a moment for the camera to initialize
    time.sleep(1)
    
    photos_taken = 0
    countdown = delay
    last_time = time.time()
    
    while photos_taken < num_photos:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame, retrying...")
            time.sleep(0.5)
            continue
        
        # Calculate countdown
        current_time = time.time()
        if current_time - last_time >= 1:
            countdown -= 1
            last_time = current_time
        
        # Add instructions and countdown to the frame
        # Create a semi-transparent overlay for text
        overlay = frame.copy()
        height, width = frame.shape[:2]
        cv2.rectangle(overlay, (0, 0), (width, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        info_text = f"Taking photo for: {name} ({photos_taken+1}/{num_photos})"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        countdown_text = f"Next photo in: {countdown} seconds" if countdown > 0 else "CAPTURING..."
        cv2.putText(frame, countdown_text, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, "Press Q to quit", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the frame
        cv2.imshow('Take Multiple Photos', frame)
        
        # Take photo when countdown reaches 0
        if countdown <= 0:
            # Save the image to the user's directory
            filename = os.path.join(user_dir, f"photo_{photos_taken+1}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Photo {photos_taken+1} saved as {filename}")
            
            # Reset countdown and increment counter
            countdown = delay
            photos_taken += 1
            
            # Flash effect to indicate photo taken
            white_frame = np.ones(frame.shape, dtype=np.uint8) * 255
            cv2.imshow('Take Multiple Photos', white_frame)
            cv2.waitKey(100)
        
        # Wait for keypress (1ms) and check if 'q' is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nQuit photo capture")
            break
    
    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nTook {photos_taken} photos for {name}")
    print(f"Photos saved in directory: {user_dir}")
    return photos_taken > 0

def ask_for_name():
    """Ask for the person's name with visual interface"""
    print("\nPlease enter the person's name:")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        # Fallback to console input if webcam fails
        return input("Enter name (use underscores for spaces): ").strip()
    
    name = ""
    instructions = [
        "Type the person's name",
        "Press ENTER when done",
        "Use BACKSPACE to correct",
        "Press ESC to cancel"
    ]
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Create a semi-transparent overlay
        overlay = frame.copy()
        height, width = frame.shape[:2]
        cv2.rectangle(overlay, (0, 0), (width, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Display title
        cv2.putText(frame, "Enter Person's Name", (width//2 - 150, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display current name
        cv2.putText(frame, name + "_", (width//2 - 100, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Display instructions
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (20, 150 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.imshow('Enter Name', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC key
            name = ""
            break
        elif key == 13:  # Enter key
            break
        elif key == 8:  # Backspace
            name = name[:-1] if name else ""
        elif 32 <= key <= 126:  # Printable ASCII characters
            name += chr(key)
    
    cap.release()
    cv2.destroyAllWindows()
    
    if not name:
        # Fallback to console input if name is empty
        return input("Enter name (use underscores for spaces): ").strip()
    
    return name

if __name__ == "__main__":
    # Default values
    name = None
    num_photos = 3
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            num_photos = int(sys.argv[2])
        except ValueError:
            print(f"Invalid number of photos: {sys.argv[2]}, using default: 3")
            num_photos = 3
    
    # If name not provided via command line, ask for it
    if not name:
        try:
            name = ask_for_name()
        except Exception as e:
            print(f"Error getting name: {str(e)}")
            # Final fallback
            name = input("Enter name (use underscores for spaces): ").strip()
    
    if not name:
        print("Error: No name provided. Exiting.")
        sys.exit(1)
    
    print(f"Taking {num_photos} photos for {name}")
    if take_multiple_photos(name, num_photos):
        print("\nPhoto capture completed. You can now restart the attendance system to recognize this person.")
    else:
        print("\nPhoto capture failed. Please check your webcam and try again.")
