import smbus
ADDR = 0x14

bus = smbus.SMBus(1)
bus.write_byte(ADDR, 0x10)
value_h = bus.read_byte(ADDR)
value_l = bus.read_byte(ADDR)
value = (value_h << 8) + value_l
print(value)