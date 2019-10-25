# ezblock
import everything
```python
from ezblock import *
```

## Methods
- `delay` - Delay for the given number of milliseconds.
```python
delay(ms)
```
- `print` - replace the original print function to print via bluetooth.
```python
print(msg, end="/n", tag='[DEBUG]')
```
- `mapping` - masp a value from a range to another
```python
mapping(x, inmin, inmax, outmin, outmax)
```

## Classes
- [class Pin - control I/O pins](Pin.md)
- [class ADC - analog to digital converter](ADC.md)
- [class PWM - pulse width modulation](PWM.md)
- [class Servo - 3-wire pwm servo driver](Servo.md)
- [class UART - serial communication bus](UART.md)
- [class I2C - IIC bus](I2C.md)
- [class Remote - remote with ble](Remote.md)
- [class IOT - internet of things](IOT.md)
- [class Music - notes and beats](Music.md)
- [class Color - rgb color](Color.md)
- [class TTS - text to speech](TTS.md)
- [class IRQ - external interrupter](IRQ.md)
- [class WiFi - Wi-Fi set up](WiFi.md)
- [class Taskmgr - task manager](Taskmgr.md)
- [class SendMail - email library](SendMail.md)
- [class Ultrasonic - ultrasonic ranging sensor](Ultrasonic.md)
- [class DS18X20 - ds18x20 series temperature sensor](DS18X20.md)
- [class ADXL345 - accelemeter](ADXL345.md)
- [class RGB_LED - rgb LED](RGB_LED.md)
- [class Buzzer - passive buzzer](Buzzer.md)
- [class Sound - sound sensor](Sound.md)
- [class Joystick - 3-axis joystick ](Joystick.md)


- [class LED - led driver](LED.md)
- [class Switch - switches](Switch.md)
- [class BLE - bluetooth driver](BLE.md)