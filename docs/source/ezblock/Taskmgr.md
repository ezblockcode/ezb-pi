# class Taskmgr - task manager

Usage:
```python
from ezblock import *

taskmgr = Taskmgr()                     # create an Taskmgr object 
temp_cpu_val = taskmgr.cpu_temperature()                    # read the temperature of CPU
temp_gpu_val = taskmgr.gpu_temperature()                    # read the temperature of GPU
cpu_usage_val = taskmgr.cpu_usage()                    # read the cpu_usage
disk_space_val = taskmgr.disk_space()                    # read the disk_space
disk_used_val = taskmgr.disk_used()                    # read the disk_used
ram_info_val = taskmgr.ram_info()                    # read the ram_info
ram_used_val = taskmgr.ram_used()                    # read the ram_used
read_val = taskmgr.read()                    # read all the systerm parameter of Pi
```
## Constructors
```class ezblock.Taskmgr(pin)```
Create an Taskmgr object to inquire the parameter of Pi.

## Methods
- cpu_temperature - inquire the temperature of CPU.
```python
Taskmgr.cpu_temperature()
```
- gpu_temperature - inquire the temperature of GPU.
```python
Taskmgr.gpu_temperature()
```
- cpu_usage - inquire the usage of CPU.
```python
Taskmgr.cpu_usage()
```
- disk_space - inquire the disk_space of Pi.
```python
Taskmgr.disk_space()
```
- disk_used - inquire the disk_space of Pi.
```python
Taskmgr.disk_used()
```
- ram_info - inquire the ram_info of Pi.
```python
Taskmgr.ram_info()
```
- ram_used - inquire the ram_used of Pi.
```python
Taskmgr.ram_used()
```
- read - inquire all the systerm parameter of Pi.
```python
Taskmgr.read()
```