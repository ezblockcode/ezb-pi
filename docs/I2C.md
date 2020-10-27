# class I2C - IIC bus

Usage:
```python
from ezblock import I2C

i2c = I2C(1)                         # create on bus 1
i2c = I2C(1, I2C.MASTER)             # create and init as a master

i2c.send('abc')      # send 3 bytes
i2c.send(0x42)       # send a single byte, given by the number
data = i2c.recv(3)   # receive 3 bytes

i2c.is_ready(0x42)           # check if slave 0x42 is ready
i2c.scan()                   # scan for slaves on the bus, returning
                             #   a list of valid addresses
i2c.mem_read(3, 0x42, 2)     # read 3 bytes from memory of slave 0x42,
                             #   starting at address 2 in the slave
i2c.mem_write('abc', 0x42, 2, timeout=1000) # write 'abc' (3 bytes) to memory of slave 0x42
                                            # starting at address 2 in the slave, timeout after 1 second
```
## Constructors
```class ezblock.I2C(num)```
Create an I2C object associated with the given num. This allows you to use i2c on that device.

## Methods
- is_ready - check if slave 0x42 is ready
```python
I2C.is_ready(addr)
```
- scan - scan for slaves on the bus, returning
```python
I2C.scan()
```
- send - send several bytes to slave with address 
```python
I2C.send(send,addr,timeout)
```
- recv - # receive one or several bytes
```python
data = i2c.recv(recv,addr,timeout)   # receive 3 bytes
```
- mem_write - Write to the memory of an I2C device
```python
I2C.mem_write(data, addr, memaddr, timeout)
```
- mem_read - Read from the memory of an I2C device
```python
I2C.mem_read(data, addr, memaddr, timeout)
```