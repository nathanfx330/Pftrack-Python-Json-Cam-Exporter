#
# Project: HoloDepth - PFTrack to models.json Exporter
# Version: 2.7 FINAL EXECUTION
# Compatibility: Python 2.7 (for legacy embedded interpreters like PFTrack)
#
import pfpy
import json
import os
import math

# ==============================================================================
# --- Mathematical Functions (Python 2, No Dependencies) ---
# ==============================================================================

def matrix_multiply(A, B):
    C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                C[i][j] += A[i][k] * B[k][j]
    return C

def euler_to_rotation_matrix(rotation):
    roll, pitch, yaw = [math.radians(angle) for angle in rotation]
    Rx = [[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]]
    Ry = [[math.cos(pitch), 0, math.sin(pitch)], [0, 1, 0], [-math.sin(pitch), 0, math.cos(pitch)]]
    Rz = [[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]]
    return matrix_multiply(Rx, matrix_multiply(Ry, Rz))

def rotation_matrix_to_axis_angle(R):
    trace = R[0][0] + R[1][1] + R[2][2]
    clipped_value = max(-1.0, min(1.0, (trace - 1.0) / 2.0))
    angle = math.acos(clipped_value)

    if abs(angle) < 1e-6:
        return [0.0, 0.0, 0.0]

    rx = R[2][1] - R[1][2]
    ry = R[0][2] - R[2][0]
    rz = R[1][0] - R[0][1]
    axis = [rx, ry, rz]
    norm = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)

    if norm < 1e-6:
      if R[0][0] > R[1][1] and R[0][0] > R[2][2]:
          t = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2.0
          axis = [t / 4.0, (R[0][1]+R[1][0]) / t, (R[0][2]+R[2][0]) / t]
      elif R[1][1] > R[2][2]:
          t = math.sqrt(1.0 - R[0][0] + R[1][1] - R[2][2]) * 2.0
          axis = [(R[0][1]+R[1][0]) / t, t / 4.0, (R[1][2]+R[2][1]) / t]
      else:
          t = math.sqrt(1.0 - R[0][0] - R[1][1] + R[2][2]) * 2.0
          axis = [(R[0][2]+R[2][0]) / t, (R[1][2]+R[2][1]) / t, t / 4.0]
      norm = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)

    axis_normalized = [c / norm for c in axis]
    axis_angle_vector = [c * angle for c in axis_normalized]
    return axis_angle_vector

# ==============================================================================
# --- Main Exporter Logic ---
# ==============================================================================

def export_for_holodepth(output_filename="models.json"):
    print "--- Starting HoloDepth Exporter ---"
    
    try:
        cam = pfpy.getCameraRef(0)
    except Exception as e:
        print "Error: Could not get PFTrack camera. Error: %s" % str(e)
        return

    start_frame = cam.getInPoint()
    end_frame = cam.getOutPoint()
    print "Processing frames %d to %d..." % (start_frame, end_frame)

    camera_data_list = []
    width = cam.getFrameWidth()
    height = cam.getFrameHeight()

    for frame_index, frame in enumerate(xrange(start_frame, end_frame + 1)):
        position = cam.getTranslation(frame)
        euler_rotation_xyz = cam.getEulerRotation(frame, 'xyz')
        focal_length_pixels = cam.getFocalLength(frame, 'pixels')
        principal_point = [width / 2.0, height / 2.0]
        rotation_matrix = euler_to_rotation_matrix(euler_rotation_xyz)
        orientation_axis_angle = rotation_matrix_to_axis_angle(rotation_matrix)

        camera_info = {
            "position": position,
            "orientation": orientation_axis_angle,
            "focal_length": focal_length_pixels,
            "principal_point": principal_point,
            "width": float(width),
            "height": float(height),
            "pixel_aspect_ratio": 1.0,
            "relative_path": "image_%02d.png" % frame_index
        }
        camera_data_list.append(camera_info)

    final_output_structure = [camera_data_list]
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(output_dir, output_filename)

    print "Data processed. Attempting to write file to: %s" % output_path
    try:
        with open(output_path, 'w') as json_file:
            json.dump(final_output_structure, json_file, indent=4)
        print "\nSUCCESS: %d camera poses exported to %s" % (len(camera_data_list), output_path)
    except IOError as e:
        print "\nERROR: Could not write to file. Check permissions. Error: %s" % str(e)
    except Exception as e:
        print "\nAn unexpected error occurred during file writing: %s" % str(e)


# ==============================================================================
# --- SCRIPT EXECUTION ---
# This line is no longer guarded by 'if __name__ == "__main__"'
# This forces the function to run as soon as PFTrack loads the script.
# This is the critical fix.
# ==============================================================================
export_for_holodepth()