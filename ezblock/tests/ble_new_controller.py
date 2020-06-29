from ezblock import Remote, delay
import random

r = Remote()
count = 0
switch = 0
# segment_test_package = [1, 99, 1234, 1.2, 33.5, 55.44, "10:25", 0.01, 0.33, "97:34"]
segment_test_package = [1, 99, 123224, 1.2, 323.522, 535.434, "10:235", 0.02221, 0.322223, "937:34"]

while True:
    r.set_segment_value("A", segment_test_package[count%len(segment_test_package)])
    # r.set_light_bolb_value("A", switch)
    # r.set_meter_value("A", count)
    # r.set_line_chart_value("A", count)
    # r.set_pie_chart_value("A", [10, 20, 30, 40])
    # r.set_bar_chart_value("A", [random.randint(0, 100) for i in range(4)])
    count += 1
    switch = switch + 1 & 1
    delay(1000)
    print(count)
