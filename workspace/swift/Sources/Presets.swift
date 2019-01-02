/*
 SwiftyGPIO

 Copyright (c) 2016 Umberto Raimondi
 Licensed under the MIT license, as follows:

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.)
 */

// MARK: - GPIOs Presets
extension SwiftyGPIO {
    // RaspberryPi 2
    // 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    static let EzBlock: [GPIOName:GPIO] = [
        .D0: RaspberryGPIO(name:"GPIO17", id:17, baseAddr:0x3F000000),
        .D1: RaspberryGPIO(name:"GPIO18", id:18, baseAddr:0x3F000000),
        .D2: RaspberryGPIO(name:"GPIO27", id:27, baseAddr:0x3F000000),
        .D3: RaspberryGPIO(name:"GPIO22", id:22, baseAddr:0x3F000000),
        .D4: RaspberryGPIO(name:"GPIO23", id:23, baseAddr:0x3F000000),
        .D5: RaspberryGPIO(name:"GPIO24", id:24, baseAddr:0x3F000000),
        .D6: RaspberryGPIO(name:"GPIO25", id:25, baseAddr:0x3F000000),
        .D7: RaspberryGPIO(name:"GPIO4", id:4, baseAddr:0x3F000000),
        .D8: RaspberryGPIO(name:"GPIO5", id:5, baseAddr:0x3F000000),
        .D9: RaspberryGPIO(name:"GPIO6", id:6, baseAddr:0x3F000000),
        .D10: RaspberryGPIO(name:"GPIO12", id:12, baseAddr:0x3F000000),
        .D11: RaspberryGPIO(name:"GPIO13", id:13, baseAddr:0x3F000000),
        .D12: RaspberryGPIO(name:"GPIO19", id:19, baseAddr:0x3F000000),
        .D13: RaspberryGPIO(name:"GPIO16", id:16, baseAddr:0x3F000000),
        .D14: RaspberryGPIO(name:"GPIO26", id:26, baseAddr:0x3F000000),
        .D15: RaspberryGPIO(name:"GPIO20", id:20, baseAddr:0x3F000000),
        .D16: RaspberryGPIO(name:"GPIO21", id:21, baseAddr:0x3F000000),
        .SW: RaspberryGPIO(name:"GPIO19", id:19, baseAddr:0x3F000000),
        .LED: RaspberryGPIO(name:"GPIO26", id:26, baseAddr:0x3F000000),
        .PWR: RaspberryGPIO(name:"GPIO12", id:12, baseAddr:0x3F000000),
        .RST: RaspberryGPIO(name:"GPIO16", id:16, baseAddr:0x3F000000),
        .BLEINT: RaspberryGPIO(name:"GPIO13", id:13, baseAddr:0x3F000000)
    ]
}
