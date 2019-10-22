# class UART - serial communication bus

Usage:
```python
from ezblock import UART

uart = UART()                      # create an UART object 
uart.init(9600)                    # uart init
uart.read(5)                       # read up 5 bytes

buf = [1,3,5]
uart.write(buf)                    # send a buf
uart.writechar('a')                # send a char
```
## Constructors
```class ezblock.UART(pin)```
Create an UART object.

## Methods
- init - init the uart.
```python
UART.init(baudrate)
```
- read - init the uart.
```python
UART.read(num)
```
- write - send a buf of bytes.
```python
UART.write(buf)
```
- writechar - send a char type byte.
```python
UART.writechar(buf)
```
