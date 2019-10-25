# class Switch - switches

Usage:
```python
from ezblock import Switch

switch = Switch("D0")                   # create an Switch object from a pin
val = switch.value()                    # read an digital value

def test:
    print("val:",val)
switch.callback(test)
```
## Constructors
```class ezblock.Switch(pin)```
Create an Switch object associated with the given pin. This allows you to then read analog values on that pin.

## Methods
- value - Read the value on the analog pin and return it. The returned value will be 0 or 1.
```python
Switch.value()
```
- callback - The irq interrupt callback function.
```python
Switch.callback()
```