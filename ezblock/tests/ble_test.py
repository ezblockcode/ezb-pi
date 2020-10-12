from ezblock import BLE, Remote, delay

ble = BLE()
r = Remote()

def test_ble():
    # buf = bytearray()
    # while ble.uart.inWaiting():
    #     buf = buf + super().read(ble.uart.inWaiting())

    # buf = buf.decode()
    # print(buf)
    print(ble.read(1))

def test_remote():
    r.read()
    print(r.get_button_value("A"))

while True:
    # test_remote()
    test_ble()
    delay(100)