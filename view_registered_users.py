import cv2
import os
import numpy as np
import sys

def view_registered_users(auto_view=True):
    """
    Display all registered users and their photos
    
    Args:
        auto_view: If True, automatically view photos without asking
    """
    print("=== Registered Users ===")
    
    # Path to known faces directory
    known_faces_dir = 'known_faces'
    
    if not os.path.exists(known_faces_dir):
        print(f"Error: {known_faces_dir} directory not found!")
        return
    
    # Get all users (both from directories and individual photos)
    users = set()
    user_photos = {}
    
    # First, check for files directly in the known_faces directory
    for filename in os.listdir(known_faces_dir):
        file_path = os.path.join(known_faces_dir, filename)
        if os.path.isfile(file_path) and filename.endswith((".jpg", ".jpeg", ".png")):
            # Extract name from filename
            name = os.path.splitext(filename)[0]
            if '_' in name and name.split('_')[-1].isdigit():
                # For files like "john_1.jpg", extract just "john"
                name = '_'.join(name.split('_')[:-1])
            
            users.add(name)
            if name not in user_photos:
                user_photos[name] = []
            user_photos[name].append(file_path)
    
    # Then, check for user directories
    for dirname in os.listdir(known_faces_dir):
        dir_path = os.path.join(known_faces_dir, dirname)
        if os.path.isdir(dir_path):
            users.add(dirname)
            if dirname not in user_photos:
                user_photos[dirname] = []
            
            # Add all photos from this user's directory
            for filename in os.listdir(dir_path):
                if filename.endswith((".jpg", ".jpeg", ".png")):
                    image_path = os.path.join(dir_path, filename)
                    user_photos[dirname].append(image_path)
    
    # Display results
    if not users:
        print("No registered users found!")
        return
    
    print(f"Found {len(users)} registered users:")
    for i, user in enumerate(sorted(users)):
        photo_count = len(user_photos[user])
        print(f"{i+1}. {user} ({photo_count} photos)")
    
    # Ask if user wants to view the photos (if not auto_view)
    view_photos = 'y'
    if not auto_view:
        try:
            view_photos = input("\nDo you want to view the photos? (y/n): ").strip().lower()
        except EOFError:
            print("\nAutomatic mode: showing photos...")
            view_photos = 'y'
    
    if view_photos != 'y':
        return
    
    # Create a grid of photos for all users
    grid_rows = len(users)
    grid_cols = max(len(photos) for photos in user_photos.values())
    
    if grid_cols > 5:  # Limit to 5 photos per user to avoid huge grids
        grid_cols = 5
    
    # Create a blank canvas for the grid
    cell_height, cell_width = 200, 200
    grid = np.ones((grid_rows * cell_height, grid_cols * cell_width, 3), dtype=np.uint8) * 255
    
    # Fill the grid with photos
    for row, user in enumerate(sorted(users)):
        photos = user_photos[user][:grid_cols]  # Limit to grid_cols photos
        
        # Add user name at the beginning of the row
        y_pos = row * cell_height + 30
        cv2.putText(grid, user, (10, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        for col, photo_path in enumerate(photos):
            try:
                img = cv2.imread(photo_path)
                if img is None:
                    continue
                
                # Resize to fit cell
                img = cv2.resize(img, (cell_width - 20, cell_height - 40))
                
                # Calculate position
                x = col * cell_width + 10
                y = row * cell_height + 40
                
                # Place in grid
                grid[y:y+img.shape[0], x:x+img.shape[1]] = img
            except Exception as e:
                print(f"Error displaying {photo_path}: {str(e)}")
    
    # Show the grid
    window_name = "Registered Users"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, grid)
    print("\nShowing all registered users. Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Check for command line arguments
    auto_view = True
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'manual':
        auto_view = False
    
    view_registered_users(auto_view)
