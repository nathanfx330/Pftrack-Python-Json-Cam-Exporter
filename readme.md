# PFTrack Python Scripting Guide: PFTrack-Python-JSON-Cam-Exporter

This guide provides instructions and best practices for writing Python scripts to automate camera and frame exports from PFTrack, aimed at preparing data for computer vision or machine learning workflows.

---

## 1. PFTrack Python API Basics

PFTrack exposes scene, camera, and lens information via the `pfpy` module.

### Getting a Camera Reference

```python
import pfpy

cam = pfpy.getCameraRef(0)  # First camera in the scene
```

### Key Camera Methods

| Method                                         | Description                              |
| ---------------------------------------------- | ---------------------------------------- |
| `cam.getTranslation(frame)`                    | Returns camera position at a given frame |
| `cam.getEulerRotation(frame, order)`           | Returns camera rotation in Euler angles  |
| `cam.getFocalLength(frame, unit)`              | Focal length in `'mm'` or `'pixels'`     |
| `cam.getFrameWidth()` / `cam.getFrameHeight()` | Frame resolution                         |
| `cam.getInPoint()` / `cam.getOutPoint()`       | Start and end frames for the camera      |

> **Note:** PFTrack cameras may not provide the actual image filename. Filenames often need to be constructed from a known prefix and padding.

---

## 2. Python Version

PFTrack scripts typically require **Python 2.7**:

* Print statements: `print "text"`
* Exception syntax: `except Exception, e:`

Python 3 features (f-strings, certain context managers) will **not** work.

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

```python
filename = "%s%04d.jpg" % ("img_", frame)  # img_0001.jpg
```

---

## 4. Handling Distortion

PFTrack lens distortion is stored in `.pfb` files.

1. Read the `.pfb` file.
2. Extract low/high order distortion and principal point.
3. Store this alongside camera data in JSON.

Ensure distortion data covers the full frame range.

---

## 5. Exporting Camera Data for Machine Learning

Typical export dictionary per frame:

```python
frame_info = {
    "width": width,
    "height": height,
    "focal_length": focal_length,
    "pixel_aspect_ratio": 1.0,
    "position": cam.getTranslation(frame),
    "orientation": orientation_vector,  # axis-angle or Euler
    "principal_point": [cx, cy],
    "relative_path": image_path
}
```

* Use **forward slashes** in file paths.
* Prefix and padding should be configurable.
* Handle missing frames gracefully.

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

* Check that the camera object supports the methods you call (`getImageFile()` may not exist).

---

## 7. Common Pitfalls

* Using Python 3 instead of Python 2.7
* Hard-coded file paths
* Incorrect frame indexing (PFTrack frames may start at 1)
* Missing images or distortion data
* Orientation math errors; convert Euler angles to matrices before axis-angle

---

## 8. Configuration Best Practices

Use constants for:

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

print "Export complete! File saved at:", output_path
```

---

## 10. Key Takeaways

1. PFTrack scripting focuses on **camera extraction, frame loops, and consistent filenames**.
2. **Debug early** — logging each frame saves time.
3. Use **configurable parameters** for paths, prefixes, and padding.
4. **Handle errors gracefully** — especially missing frames or distortion values.
5. Export JSON with **forward slashes** for cross-platform compatibility.

---

This guide provides a solid foundation for creating robust PFTrack Python scripts for camera exports and dataset preparation.
