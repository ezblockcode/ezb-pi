# class Servo - 3-wire pwm servo driver

Usage:
```python
from ezblock import Servo, PWM

pin = PWM("P0")
ser = Servo(pin)                      # create an Servo object from a pin
val = ser.angle(60)                   # set the servo angle
```
## Constructors
```class ezblock.Servo(pin)```
Create an Servo object associated with the given pin. This allows you to set the angle values.

## Methods
- angle - set the angle values between -90 and 90.
```python
Servo.angle(90)
```