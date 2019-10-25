# class Color - rgb color

Usage:
```python
from ezblock import Color

c = Color()                                      # create an color object
white = c.color("#ffffff")                       # hex color
white_led = c.led_color("#ffffff")               # hex color for led
color_red = c.get_from("red", "#ffffff")         # get red from a rgb color
random_color = c.random()                        # get random color
color = c.rgb(200, 20, 40)                       # get color from RGB value
blended = c.blend("#ff0000", "#00ff00", 0.5)     # blend 2 color with specific ratio 
```
## Constructors
```class ezblock.Color()```
Create an Color object. This allows you to then get or control colors!

## Methods
- `color` - get color from a hex string. this function only test the value if is color format, then returns the input value.
```python
Color().color("#88ff44")
```
- `led_color` - get color from a hex string. this function only test the value if is color format, then returns the input value. same as `color()`
```python
Color().led_color("#88ff44")
```
- `get_from` - get Red/Green/Blue value from a color.
```python
Color().get_from("red", "#88ff44")
```
- `random` - get random color.
```python
Color().random()
```
- `rgb` - get color from RGB value. ranlue ranges 0~255.
```python
Color().rgb(200,100,20)
```
- `blend` - blend two color with specific ratio. Ratio ranges 0~1, float
```python
Color().blend("#ff0000", "#00ff00", 0.5)
```