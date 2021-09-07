from ezblock import BLE, Remote, delay

ble = BLE()
r = Remote()

def test_read():
    print(ble.read(1))

def test_inWaiting():
    buf = bytearray()
    while ble.uart.inWaiting():
        buf += ble.read(ble.uart.inWaiting())

    buf = buf.decode()
    print(buf)

def test_remote():
    r.read()
    print(r.get_button_value("A"))

while True:
    test_read()
    # test_inWaiting()
    delay(100)