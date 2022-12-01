# class UART - serial communication bus

Usage:
```python
from ezblock import UART

# On Raspberry Pi and init later
uart = UART("/dev/serial0")        # create an UART object
uart.init(9600)                    # uart init
uart.read(5)                       # read up 5 bytes

# On Ezblock One and init
uart = UART(1, tx=25, rx=26, baudrate=115200)    # create an UART object
buf = [1,3,5]
buf = bytearray(buf)
uart.write(buf)                                  # send a buf
```
## Constructors
```class ezblock.UART(device, tx=None, rx=None, baudrate=115200)```
Create an UART object.
device: On Ezblock Pi, it's the serial path, like: /dev/xxx().
  On Ezblock One, it's the uart id: 0, 1, 2
tx: pin of tx.
rx: pin of rx

## Methods
- init - init the uart.
```python
UART.init(baudrate)
```
- read - read data.
```python
UART.read(num)
```
- write - send a buf of bytes.
```python
UART.write(buf)
```