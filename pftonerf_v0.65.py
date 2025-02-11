import pfpy  # PFTrack Python API
import json
import os
import math

# Path to the .pfb file (pf barrel) distortion file (remember to delete the header text)
DISTORTION_FILE_PATH = r"path to... distortion.pfb"

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

def euler_to_rotation_matrix(rotation):
    """Convert Euler rotation to a 3x3 rotation matrix."""
    roll, pitch, yaw = rotation  # Assuming the order is roll, pitch, yaw
    
    # Convert degrees to radians
    roll = math.radians(roll)
    pitch = math.radians(pitch)
    yaw = math.radians(yaw)

    # Rotation matrices around the X, Y, Z axes
    Rx = [[1, 0, 0],
          [0, math.cos(roll), -math.sin(roll)],
          [0, math.sin(roll), math.cos(roll)]]
    
    Ry = [[math.cos(pitch), 0, math.sin(pitch)],
          [0, 1, 0],
          [-math.sin(pitch), 0, math.cos(pitch)]]
    
    Rz = [[math.cos(yaw), -math.sin(yaw), 0],
          [math.sin(yaw), math.cos(yaw), 0],
          [0, 0, 1]]
    
    # Combine the rotations
    rotation_matrix = matrix_multiply(Rx, matrix_multiply(Ry, Rz))
    return rotation_matrix

def matrix_multiply(A, B):
    """Multiplies two 3x3 matrices."""
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def build_transform_matrix(rotation_matrix, translation):
    """Constructs a 4x4 transformation matrix from rotation and translation."""
    # Rotation matrix already gives us the top-left 3x3 part
    transform_matrix = [
        [rotation_matrix[0][0], rotation_matrix[0][1], rotation_matrix[0][2], translation[0]],
        [rotation_matrix[1][0], rotation_matrix[1][1], rotation_matrix[1][2], translation[1]],
        [rotation_matrix[2][0], rotation_matrix[2][1], rotation_matrix[2][2], translation[2]],
        [0.0, 0.0, 0.0, 1.0]  # Homogeneous coordinate row
    ]
    return transform_matrix

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

            # Check if PFTrack provides a direct transformation matrix method
            transform_matrix = cam.getTransformMatrix(frame)  # Hypothetical method

            if transform_matrix is None:
                # If there's no direct method, construct it manually using translation and rotation
                rotation_matrix = euler_to_rotation_matrix(rotation)  # Convert euler rotation to matrix
                transform_matrix = build_transform_matrix(rotation_matrix, translation)

            camera_angle_x = 2 * math.atan(width / (2 * focal_length))
            camera_angle_y = 2 * math.atan(height / (2 * focal_length))

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
