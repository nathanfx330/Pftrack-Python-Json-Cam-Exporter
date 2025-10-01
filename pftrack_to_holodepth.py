#
# Project: HoloDepth - PFTrack Exporter
# Version: 3.0 FINAL (Python 2, Correct Pathing)
#
import pfpy
import json
import os
import math

# (All the math functions remain the same as the last version)
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
    if abs(angle) < 1e-6: return [0.0, 0.0, 0.0]
    rx, ry, rz = R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]
    axis = [rx, ry, rz]
    norm = math.sqrt(sum(c**2 for c in axis))
    if norm < 1e-6:
        # Stable fallback for 180 degree rotation
        if R[0][0] > R[1][1] and R[0][0] > R[2][2]:
            t = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2.0; axis = [t / 4.0, (R[0][1]+R[1][0]) / t, (R[0][2]+R[2][0]) / t]
        elif R[1][1] > R[2][2]:
            t = math.sqrt(1.0 - R[0][0] + R[1][1] - R[2][2]) * 2.0; axis = [(R[0][1]+R[1][0]) / t, t / 4.0, (R[1][2]+R[2][1]) / t]
        else:
            t = math.sqrt(1.0 - R[0][0] - R[1][1] + R[2][2]) * 2.0; axis = [(R[0][2]+R[2][0]) / t, (R[1][2]+R[2][1]) / t, t / 4.0]
        norm = math.sqrt(sum(c**2 for c in axis))
    axis_normalized = [c / norm for c in axis]
    return [c * angle for c in axis_normalized]


def export_for_holodepth(scene_name, image_extension="jpg", output_filename="models.json"):
    print "--- Starting HoloDepth Exporter V3 ---"
    
    try: cam = pfpy.getCameraRef(0)
    except: print "Error: Could not get PFTrack camera."; return

    start_frame, end_frame = cam.getInPoint(), cam.getOutPoint()
    print "Processing %s from frame %d to %d..." % (scene_name, start_frame, end_frame)

    camera_data_list = []
    width, height = cam.getFrameWidth(), cam.getFrameHeight()

    for frame_index, frame in enumerate(xrange(start_frame, end_frame + 1)):
        # ======================================================================
        # THE FIX: Generate the relative_path to match your actual files
        # ======================================================================
        relative_path = "%s_%04d.%s" % (scene_name, frame_index, image_extension)
        
        camera_info = {
            "position": cam.getTranslation(frame),
            "orientation": rotation_matrix_to_axis_angle(euler_to_rotation_matrix(cam.getEulerRotation(frame, 'xyz'))),
            "focal_length": cam.getFocalLength(frame, 'pixels'),
            "principal_point": [width / 2.0, height / 2.0],
            "width": float(width),
            "height": float(height),
            "pixel_aspect_ratio": 1.0,
            "relative_path": relative_path
        }
        camera_data_list.append(camera_info)

    final_output = [camera_data_list]
    output_path = os.path.join(os.path.expanduser("~"), "Desktop", output_filename)

    try:
        with open(output_path, 'w') as f:
            json.dump(final_output, f, indent=4)
        print "\nSUCCESS: Exported %s for %d frames to Desktop." % (output_filename, len(camera_data_list))
    except Exception as e:
        print "\nERROR: Could not write file. Error: %s" % str(e)
