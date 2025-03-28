import cv2
import os
import sys

def take_photo(name):
    print(f"\nTaking photo for {name}")
    print("Position the person in front of the camera")
    print("Press SPACE to capture the photo or Q to quit")
    
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        return False
        
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Add instructions to the frame
        cv2.putText(frame, f"Taking photo for: {name}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE: Capture  Q: Quit", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the frame
        cv2.imshow('Take Photo', frame)
        
        # Wait for keypress
        key = cv2.waitKey(1) & 0xFF
        
        # If space bar is pressed, save the image
        if key == ord(' '):
            # Save the image
            filename = os.path.join('known_faces', f'{name}.jpg')
            cv2.imwrite(filename, frame)
            print(f"\nPhoto saved as {filename}")
            break
        
        # If 'q' is pressed, quit without saving
        elif key == ord('q'):
            print("\nQuit without saving")
            break
    
    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = input("\nEnter the person's name (use underscores for spaces): ").strip()
    
    if name:
        if take_photo(name):
            print("\nPhoto capture completed. You can now restart the attendance system to recognize this person.")
