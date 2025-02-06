import pfpy  # PFTrack Python API
import json
import os

def create_and_export_camera_keyframes(output_json="cameras.json"):
    # Get the animated camera (assumed to be the first camera)
    cam = pfpy.getCameraRef(0)
    
    # Retrieve the keyframe range using the camera's in point and out point
    start_frame = cam.getInPoint()   # e.g., first keyed frame
    end_frame = cam.getOutPoint()      # e.g., last keyed frame
    
    print("Camera in point: {0}, out point: {1}".format(start_frame, end_frame))
    
    cameras_data = []
    
    # Loop over each frame in the keyframe range
    for frame in range(start_frame, end_frame + 1):
        # Optionally, if your environment requires it, you might set the current frame:
        # pfpy.setCurrentFrame(frame)
        
        # Extract camera parameters for this frame
        translation = cam.getTranslation(frame)          # (x, y, z)
        rotation = cam.getEulerRotation(frame, 'xyz')      # (x, y, z) in degrees
        focal_length = cam.getFocalLength(frame, 'mm')       # in millimeters
        fov = cam.getHorizontalFOV(frame, 'deg')           # Horizontal FOV in degrees
        name = cam.getName()  # This likely stays the same for an animated camera
        
        # Store the data in a dictionary
        camera_info = {
            "camera_name": "camera_{0}_{1}".format(frame, name),
            "frame": frame,
            "fov": fov,
            "focal_length": focal_length,
            "translation": translation,
            "rotation": rotation
        }
        cameras_data.append(camera_info)
    
    # Define the output path on the Desktop
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(output_dir):
        print("Error: The directory does not exist: {0}".format(output_dir))
        return

    output_path = os.path.join(output_dir, output_json)
    
    # Write the camera keyframe data to the JSON file
    try:
        with open(output_path, 'w') as json_file:
            json.dump(cameras_data, json_file, indent=4)
        print("{0} frames exported to {1}.".format(len(cameras_data), output_path))
    except IOError as e:
        print("Error writing to file {0}: {1}".format(output_path, e))

# Export camera keyframe data to JSON
create_and_export_camera_keyframes("cameras.json")
