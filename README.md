# Pftrack-Python-Json-Cam-Exporter
This repository provides a Python node for PFTrack to export camera data as a JSON file. The exporter extracts keyframe information such as translation, rotation, focal length, and field of view (FOV) for each frame in the animated camera's sequence.

    Export Camera Data: Extracts keyframe data including translation, rotation, focal length, and FOV.
    Frame Iteration: Loops through all frames between the camera's in and out points.
    Customizable Output: Outputs the data as a JSON file on your desktop with a customizable name.
    Integration: Works as a Python node in PFTrack, utilizing PFTrack's Python API.

Requirements

    PFTrack (with Python node support)
    Python 3.x
    PFTrack's Python API (pfpy)

Usage

   Loads into the Python Node in PF Track Placed after a Camera Solve or Survey Solve
