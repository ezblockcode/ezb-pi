# class RGB_LED - rgb LED

Usage:
```python
from ezblock import *

rgb = RGB_LED("P0","P1","P2")                     # create an RGB_LED object from a pin
val = rgb.write('#FFFFFF')                   # write value of value
```
## Constructors
```class ezblock.RGB_LED(Rpin, Gpin, Bpin)```
Create an RGB_LED object associated with the given pin. This allows you set the color of RGB_LED.

## Methods
- write - Read the value on the analog pin and return it. The returned value will be between 0 and 4095.
```python
RGB_LED.write(color)
```
