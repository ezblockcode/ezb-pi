# class IOT - internet of things

Usage:
```python
from ezblock import IOT

iot = IOT()
```
## Constructors
```class ezblock.IOT(iot_token, device)```
Create an ADC object associated with the given pin. This allows you to then read analog values on that pin.

## Methods
- post - 1
```python
IOT.post(sensorname, value)
```
- get - 1
```python
IOT.get(sensorname)
```