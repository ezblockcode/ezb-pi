# class RGB - RGB matrix screen by i2c

Usage:
```python
from ezblock import *
from map import Alphabet, Icons

rr = RGB_Matrix(0X74)  #create an rgb matrix object,0X74 is screen device address
for pos in range(40):
    rr.show_string("helloworld", "#842154", pos=pos)  #Scroll display 'hello world','#842154' Corresponding R.G.B color and pos is display string position
    time.sleep(0.5)
rr.show_icon("happy", "#F0F00F")  #display happy icon
```

## Constructors
```class ezblock.RGB_Matrix(0X74)```
Create an RGB Matrix screen object.This screen size is 8x8 and it has 64 RGB LEDs,set R.G.B corresponding PWM value to control each LED color,and then display various images.

## Methods
- init - init the rgb matrix
```python
RGB_Matrix.init(addr)  #addr is screen device address
```
- write_cmd
```python
RGB_Matrix.write_cmd(reg, cmd)
```
- write_Ndata - Write multiple data
```python
RGB_Matrix.write_Ndata(startaddr, data, length)
```
- image - write data to screen
```python
RGB_Matrix.image(image)  #image is list of data
```
- display_char
```python
RGB_Matrix.display_char(data, color)
```
- string_to_string_bits - String to display bit
```python
RGB_Matrix.string_to_string_bits(string)
```
- string_to_bytes
```python
RGB_Matrix.string_to_bytes(s, pos=0)  #pos is display string position
```
- string_bits_to_bytes
```python
RGB_Matrix.string_bits_to_bytes(_bits_list)
```
- show_string
```python
RGB_Matrix.show_string(string, color, pos=0)  #pos is display string position
```
- show_icon
```python
RGB_Matrix.show_icon(icon, color)
```

