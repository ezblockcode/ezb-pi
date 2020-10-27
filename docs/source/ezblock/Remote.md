# class Remote - remote with ble

Usage:
```python
from ezblock import Remote

remote = Remote()                       # create an Remote object from
val = remote.read()                     # read an analog value

slider_val = remote.get_slider_value()  # get slider value
```
## Constructors
```class ezblock.Remote()```
Create an Remote object associated with the device.

## Methods
- read - Read the name and value of device.
```python
Remote.read()
```
- get_value - get the value of device.
```python
Remote.get_value()
```
- get_joystick_value - get the joystick_value of device.
```python
Remote.get_joystick_value()
```
- get_slider_value - get the slider_value of device.
```python
Remote.get_slider_value()
```
- get_dpad_value - get the dpad_value of device.
```python
Remote.get_dpad_value()
```
- get_button_value - get the button_value of device.
```python
Remote.get_button_value()
```
- get_switch_value - get the switch_value of device.
```python
Remote.get_switch_value()
```