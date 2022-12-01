# class NRF24 - NRF24L01 communication module

Usage:

```python
from ezblock import NRF24
#write mode
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]
radio = NRF24()
radio.begin(0, 0, 25, 18)  #Initialize SPI bus and Set CE and IRQ pins
radio.setRetries(15,15)  #set max retries
radio.setPayloadSize(8)  #set send byte size max is 32
radio.setChannel(0x60)  #set nrf24 channel
radio.setDataRate(NRF24.BR_250KBPS)  #set send data rate
radio.setPALevel(NRF24.PA_MAX)  #set PA Levels
radio.setAutoAck(1)  #open auto ack
radio.openWritingPipe(pipes[1])  #open write pipe
radio.openReadingPipe(1, pipes[0])  #open read pipe
radio.startListening()
radio.stopListening()
radio.printDetails()  #print details
radio.write([6,6,6])  #send data
#read mode
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]
radio = NRF24()
radio.begin(0, 0, 25, 18)
radio.setRetries(15,15)
radio.setPayloadSize(8)
radio.setChannel(0x60)
radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(1)
radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.startListening()
radio.stopListening()
radio.printDetails()
radio.startListening()
while True：
    while not radio.available(pipe, True, irq_timeout=1000):
            print("not avaiable")
            time.sleep(1000/1000000.0)
    recv_buffer = []
    radio.read(recv_buffer)  #read data
```

## Constructors

```class ezblock.NRF24()```
Create an nrf24l01 object,this s a single chip radio transceiver for the world wide 2.4 - 2.5 GHz ISMband.Output power, frequency channels, and protocol setup are easily programmable through a SPI interface.

## Methods

- begin - Initialize SPI bus and set CE and IRQ pins

```python
NRF24.begin(major, minor, ce_pin, irq_pin)
```

- setRetries - set max retries

```python
NRF24.setRetries(delay, count)
```

- setPayloadSize - set send byte size max is 32

```python
NRF24.setPayloadSize(size)
```

- setChannel

```python
NRF24.setChannel(channel)
```

- setDataRate

```python
NRF24.setDataRate(speed)
```

- setPALevel

```python
NRF24.setPALevel(level)
```

- setAutoAck

```python
NRF24.setAutoAck(enable)
```

- openWritingPipe

```python
NRF24.openWritingPipe(value)
```

- openReadingPipe

```python
NRF24.openReadingPipe(pipe, address)
```

- startListening

```python
NRF24.startListening()
```

- stopListening

```python
NRF24.stopListening()
```

- printDetails - print details

```python
NRF24.printDetails()
```

- irqWait - Block program until falling edge is detected

```python
NRF24.irqWait(timeout=30000)
```

- available - Check whether data is received

```python
NRF24.available(pipe_num=None, irq_wait=False, irq_timeout=30000)
```

- read_register

```python
NRF24.read_register(reg, length=1)
```

- write_register - Write register value

```python
NRF24.write_register(reg, value)
```

- write_payload - Writes data to the payload register, automatically padding it to match the required length

```python
NRF24.write_payload(buf)
```

- read_payload - Reads data from the payload register and sets the DR bit of the STATUS register

```python
NRF24.read_payload(buf, buf_len=-1)  #if len Less than zero,len equal to the size of the sent data
```

- write - send data

```python
NRF24.write(buf)
```

- read - receive data

```python
NRF24.read(buf, buf_len=-1)  #if len Less than zero,len equal to the size of the sent data
```

- reset

```python
NRF24.reset()
```
