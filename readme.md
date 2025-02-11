# Pftrack Python Json Cam Exporter

This repository provides a Python node for PFTrack to export camera data as a JSON file. The exporter extracts keyframe information such as translation, rotation, focal length, and field of view (FOV) for each frame in the animated camera's sequence.

New: PFtoNERF. 
A script designed to export PFTrack's Photo Survey camera solve and variable focus undistort (exported as PF Barrel) and generate a Nerfstudio-compatible transforms.json. (Currently working on solving sharpness values.)

This is a foundational project that will serve as a stepping stone for developing the next version, which will generate the `transforms.json` file for NerfStudio.

## Features

- **Export Camera Data**: Extracts keyframe data including translation, rotation, focal length, and FOV.
- **Frame Iteration**: Loops through all frames between the camera's in and out points.
- **Customizable Output**: Outputs the data as a JSON file on your desktop with a customizable name.
- **Integration**: Works as a Python node in PFTrack, utilizing PFTrack's Python API.

## Usage

Loads into the Python Node in PFTrack, placed after a Camera Solve or Survey Solve.
