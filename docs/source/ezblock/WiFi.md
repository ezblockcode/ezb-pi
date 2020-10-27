# class WiFi - Wi-Fi set up

Usage:
```python
from ezblock import WiFi

wifi = WiFi()                     # create an WiFi object 
wifi.write('CN','sunfounder','sunfounder')
```
## Constructors
```class ezblock.WiFi(pin)```
Create an WiFi object to connect internet.

## Methods
- write - write the imformation of wifi then will connect the wifi.
```python
WiFi.write()
```