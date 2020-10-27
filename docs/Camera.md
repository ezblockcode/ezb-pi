# class Camera - camera module

Usage:

```python
from ezblock import Camera

cam = Camera()                                   # create an camera object
cam.start()                                      # start camera streaming
cam.stop()                                       # stop camera streaming
```

## Constructors

```class ezblock.Camera(res=1, fps=12, port=9000, rotation=0)```
Create an Camera object. This allows you to then control the camera!

- `res` resolution. 0: 320x240, 1: 640x480, 2: 1024x576, 3: 1280x800, default to 1
- `fps` frame per second. default to 12
- `port` Streaming port, default to 9000 for ezblock remote panel
- `rotation` rotation of the video.

## Methods

- `start` - start video streaming value.

```python
Camera().start()
```

- `stop` - stop video streaming`

```python
Camera().stop()
```
