# class LED - led driver

Usage:
```python
from ezblock import LED

led = LED()                     # create an led object
led.on()
led.off()

led.pwm_on()
led.pwm_off()
```
## Constructors
```class ezblock.LED()```
The LED object controls an individual LED (Light Emitting Diode).

## Methods
- on - Turn the LED on, to maximum intensity.
```python
LED.on()
```
- off - Turn the LED off.
```python
LED.off()
```
- pwm_on - Turn on the LED pwm mode.
```python
LED.on()
```
- pwm_off - Turn off the LED pwm mode.
```python
LED.pwm_off()
```
- intensity - Get or set the LED intensity. Intensity ranges between 0 (off) and 255 (full on). If no argument is given, return the LED intensity. If an argument is given, set the LED intensity and return 
```python
LED.intensity(*value)
```