````markdown
# PFTrack Python Scripting Guide: 
Pftrack-Python-Json-Cam-Exporter 

This guide provides instructions and best practices for writing Python scripts to automate camera and frame exports from PFTrack. It is aimed at users who want to extract camera parameters, handle lens distortion, or prepare data for downstream applications like computer vision or machine learning.

---

## 1. PFTrack Python API Basics

PFTrack exposes most scene, camera, and lens information via the `pfpy` module.

### Getting a camera reference
```python
import pfpy

cam = pfpy.getCameraRef(0)  # Get the first camera in the scene
````

### Key camera methods

* `cam.getTranslation(frame)` → returns camera position at a given frame
* `cam.getEulerRotation(frame, order)` → returns camera rotation in Euler angles
* `cam.getFocalLength(frame, unit)` → focal length (`'mm'` or `'pixels'`)
* `cam.getFrameWidth()` / `cam.getFrameHeight()` → frame resolution
* `cam.getInPoint()` / `cam.getOutPoint()` → first and last frame of the camera

> **Note:** PFTrack cameras may not provide the actual image filename. You may need to construct filenames from a known prefix and padding.

---

## 2. Python Version

PFTrack scripts typically require **Python 2.7**:

* Print statements use: `print "text"`
* Exception syntax: `except Exception, e:`

Some Python 3 features (f-strings, certain context managers) will not work.

---

## 3. Looping Through Frames

Always get the camera frame range:

```python
start, end = cam.getInPoint(), cam.getOutPoint()

for frame in xrange(start, end + 1):
    pos = cam.getTranslation(frame)
    rot = cam.getEulerRotation(frame, 'xyz')
```

### Frame Numbering

To create consistent image filenames:

```python
filename = "%s%04d.jpg" % ("img_", frame)  # img_0001.jpg
```

---

## 4. Handling Distortion

PFTrack lens distortion is stored in `.pfb` files.

1. Read the `.pfb` file.
2. Extract low/high order distortion and principal point.
3. Store this information alongside camera data in JSON.

Always verify that distortion data covers the full frame range.

---

## 5. Exporting Camera Data for Machine Learning

Typical export dictionary structure per frame:

```python
frame_info = {
    "width": width,
    "height": height,
    "focal_length": focal_length,
    "pixel_aspect_ratio": 1.0,
    "position": cam.getTranslation(frame),
    "orientation": orientation_vector,  # usually axis-angle or Euler
    "principal_point": [cx, cy],
    "relative_path": image_path
}
```

* Use **forward slashes** in file paths for JSON portability.
* Prefix and padding should be configurable.
* Handle missing frames gracefully (log warnings and continue).

---

## 6. Debugging Tips

* Print progress per frame:

```python
print "Frame %d -> using image: %s" % (frame, filename)
```

* Flush output in long loops:

```python
import sys
sys.stdout.flush()
```

* Verify the camera object supports the methods you call (`getImageFile()` may not exist).

---

## 7. Common Pitfalls

* Using Python 3 instead of Python 2.7.
* Hard-coded file paths.
* Incorrect frame indexing (PFTrack frames may start at 1, not 0).
* Missing images or distortion data.
* Orientation math errors; convert Euler angles to matrices before axis-angle.

---

## 8. Configuration Best Practices

Use constants for:

* Image folder path
* Sequence prefix
* Sequence padding
* Image file extension

Example:

```python
IMAGE_FOLDER = r"C:/MySequence"
SEQUENCE_PREFIX = "img_"
SEQUENCE_PADDING = 4
EXT = "jpg"
```

---

## 9. Example Skeleton Script

```python
import pfpy, os, json

# Configuration
IMAGE_FOLDER = r"C:/MySequence"
SEQUENCE_PREFIX = "img_"
SEQUENCE_PADDING = 4
EXT = "jpg"

cam = pfpy.getCameraRef(0)
start, end = cam.getInPoint(), cam.getOutPoint()

frames_data = []

for frame in xrange(start, end + 1):
    filename = "%s%0*d.%s" % (SEQUENCE_PREFIX, SEQUENCE_PADDING, frame, EXT)
    filename_path = os.path.join(IMAGE_FOLDER, filename).replace("\\","/")
    frames_data.append({
        "position": cam.getTranslation(frame),
        "orientation": cam.getEulerRotation(frame, 'xyz'),
        "relative_path": filename_path
    })

output_path = os.path.join(os.path.expanduser("~"), "Desktop", "models.json")

with open(output_path, 'w') as f:
    json.dump([frames_data], f, indent=4)
```

---

## 10. Key Takeaways

1. PFTrack scripting is mostly about **camera extraction, frame loops, and consistent filenames**.
2. **Debug early** — logging each frame saves hours.
3. Use **configurable parameters** for paths, prefixes, and padding.
4. **Handle errors gracefully**, especially missing frames or distortion values.
5. Export JSON with **forward slashes** for cross-platform compatibility.

---

This guide should help you quickly write reliable PFTrack Python scripts for exporting camera data and frame sequences.

```

---

If you want, I can also create a **version with visuals and example JSON output** embedded for GitHub, which helps new users immediately see the structure.  

Do you want me to do that next?
```
