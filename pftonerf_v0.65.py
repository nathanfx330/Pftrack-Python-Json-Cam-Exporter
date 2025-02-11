import pfpy  # PFTrack Python API
import json
import os
import math

# Path to the PF barrel pfb distortion file, remember delete header text.
DISTORTION_FILE_PATH = r"path to..\distortion.pfb"

def read_distortion_file(file_path):
    """Reads the distortion file, filtering out non-numeric lines and extracting relevant values."""
    if not os.path.exists(file_path):
        print("Error: Distortion file not found: {0}".format(file_path))
        return None

    distortion_values = []

    with open(file_path, "r") as file:
        lines = [line.strip() for line in file if line.strip()]  # Remove empty lines

    # Debug: Print out the first few lines for verification
    print("First 10 lines from distortion file:", lines[:10])

    try:
        i = 0
        while i < len(lines):
            try:
                frame_number = int(lines[i])  # Frame number
                low_order = float(lines[i + 1])  # Low Order
                high_order = float(lines[i + 2])  # High Order
                cx = float(lines[i + 3])  # Frame center X (normalized)
                cy = float(lines[i + 4])  # Frame center Y (normalized)
                
                distortion_values.append((low_order, high_order, cx, cy))
                i += 5  # Move to the next frame block
                
            except ValueError as e:
                print("Skipping invalid line: {0}".format(lines[i]))
                i += 1  # Skip the problematic line and continue
        
        # Debug: Print some extracted values
        print("Extracted Distortion Values (First 5):", distortion_values[:5])

        return distortion_values

    except Exception as e:
        print("Error: Could not extract all distortion values correctly. Error details: {0}".format(str(e)))
        return None


def create_and_export_camera_keyframes(output_json="transform.json"):
    """Extracts camera keyframes and exports them to a JSON file in the transform.json format."""
    
    # Read distortion values
    distortion_values = read_distortion_file(DISTORTION_FILE_PATH)
    if distortion_values is None:
        print("Error: Could not retrieve distortion values. Exiting.")
        return

    # Get the first camera
    cam = pfpy.getCameraRef(0)
    start_frame = cam.getInPoint()
    end_frame = cam.getOutPoint()

    print("Camera in point: {0}, out point: {1}".format(start_frame, end_frame))

    frames_data = []
    width = cam.getFrameWidth()
    height = cam.getFrameHeight()

    # Process each frame in the keyframe range
    for frame in range(start_frame, end_frame + 1):
        try:
            low_order, high_order, cx, cy = distortion_values[frame - start_frame]

            # Extract camera parameters for this frame
            translation = cam.getTranslation(frame)
            rotation = cam.getEulerRotation(frame, 'xyz')
            focal_length = cam.getFocalLength(frame, 'mm')  # **FIXED**
            fov = cam.getHorizontalFOV(frame, 'deg')

            camera_angle_x = 2 * math.atan(width / (2 * focal_length))
            camera_angle_y = 2 * math.atan(height / (2 * focal_length))

            transform_matrix = [
                [0.860, -0.045, -0.508, translation[0]],
                [-0.510, -0.047, -0.859, translation[1]],
                [0.015, 0.998, -0.064, translation[2]],
                [0.0, 0.0, 0.0, 1.0]
            ]

            # Store frame data in the correct format for NeRF Studio
            frame_info = {
                "w": width,
                "h": height,
                "fl_x": focal_length,
                "fl_y": focal_length,
                "camera_angle_x": camera_angle_x,
                "camera_angle_y": camera_angle_y,
                "cx": cx * width,  # Convert to pixel coordinates
                "cy": cy * height,
                "k1": low_order,
                "k2": high_order,
                "k3": 0,  # You can extend this to add k3 or other values if needed
                "transform_matrix": transform_matrix,
                "file_path": "export/photo_{0}.jpg".format(frame),
                "sharpness": 1891.379061271359  # Assuming a default sharpness value
            }
            frames_data.append(frame_info)

        except IndexError:
            print("Warning: Skipping frame {0} due to missing distortion values.".format(frame))
            continue

    # Define the output directory (Desktop)
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(output_dir):
        print("Error: The directory does not exist: {0}".format(output_dir))
        return

    output_path = os.path.join(output_dir, output_json)

    # Write the camera keyframe data to the JSON file
    try:
        with open(output_path, 'w') as json_file:
            json.dump({"aabb_scale": 16, "frames": frames_data}, json_file, indent=4)
        print("{0} frames exported to {1}.".format(len(frames_data), output_path))
    except IOError as e:
        print("Error writing to file {0}: {1}".format(output_path, str(e)))


# Export camera keyframe data to JSON in the NeRF transform.json format
create_and_export_camera_keyframes("transform.json")
