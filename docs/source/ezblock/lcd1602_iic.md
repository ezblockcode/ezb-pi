# class LCD - LCD1602 by iic

Usage:
```python
from ezblock import *

lcd = LCD(0X27)            #create an LCD object,0X27 is screen device address
lcd.write(4, 0, 'Hello')   #display 'hello' at the fourth place line 0
lcd.write(7, 1, 'world!')  #display 'world!' at the seventh place line 1
```

## Constructors
```class ezblock.LCD(0X27)```
LCD1602, is a kind of dot matrix module to show letters, numbers, and characters and so on. The model 1602 means it displays 2 lines of 16 characters.

## Methods
- init - init the lcd
```python
LCD.init(addr, blen=1)  #addr is screen device address blen is backlight
```
- write_word - iic write
```python
LCD.write_word(data)
```
- send_command
```python
LCD.send_command(cmd)
```
- send_data
```python
LCD.send_data(data)
```
- clear - Clear Screen
```python
LCD.clear()
```
- openlight - Enable the backlight
```python
LCD.openlight()
```
- write - write string to screen
```python
LCD.write(x, y, str)
```
- message - write text to screen automatic line feed
```python
LCD.message(text)
```