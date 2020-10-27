# class ADC - analog to digital converter

Usage:
```python
from ezblock import ADC

adc = ADC("A0")                     # create an analog object from a pin
val = adc.read()                    # read an analog value
```
## Constructors
```class ezblock.ADC(pin)```
Create an ADC object associated with the given pin. This allows you to then read analog values on that pin.

## Methods
- read - Read the value on the analog pin and return it. The returned value will be between 0 and 4095.
```python
ADC.read()
```