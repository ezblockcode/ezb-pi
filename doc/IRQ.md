# class IRQ - external interrupter

Usage:
```python
from ezblock import IRQ

def callback(line):
    print("line =", line)
irq = IRQ('D1',IRQ.IRQ_RISING,callback('D1'))
```
## Constructors
```class ezblock.IRQ(pin, trigger, callback)```
Create an IRQ object associated with the given pin. 

## Methods
- `disable` - Disable the interrupt associated with the ExtInt object. This could be useful for debouncing.
```python
IRQ.disable()
```
- enable - Enable a disabled interrupt.
```python
IRQ.enable()
```
- line - Return the line number that the pin is mapped to.
```python
IRQ.line()
```
- swint - Trigger the callback from software.
```python
IRQ.swint()
```

## Constance
- `IRQ_FALLING` - 0
- `IRQ_FALLING` - 
- `IRQ_FALLING` - 
