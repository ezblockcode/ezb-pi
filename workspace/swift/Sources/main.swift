/*
import SwiftyGPIO
import Foundation
// Get a dictionary of all the gpio pins
let gpios = SwiftyGPIO.GPIOs(for: .RaspberryPi3)
// Get the pin that you connected the LED to. Remember to set the right pin number, for me it was 27
guard let ledGpio = gpios[GPIOName.P26] else {
    fatalError("Could not initialize the gpio")
}
// Set the pin direction to .OUT and turn it off
ledGpio.direction = .OUT
ledGpio.value = 0
// Read user input from keyboard and switch the LED on/off each time the user presses the return key
print("Press return to switch the LED on/off. To quit type exit")
while let userInput = readLine(strippingNewline: true), userInput != "exit" {
    print("Switching LED")
    ledGpio.value = ledGpio.value == 0 ? 1 : 0
}
*/


// import Foundation
// extension SwiftyGPIO {
//     let gpios = SwiftyGPIO.GPIOs(for:.Ezblock)
//     gpios[.P17]!.direction = .OUT
// }
//     while true {    
//         gpios[.P17]!.value = 1
//         gpios[.P17]!.value = 0
//     }
 
// PIN test
// import Foundation
// let gpios = SwiftyGPIO.GPIOs()
// let ledGpio = gpios[.D0]!
// ledGpio.direction = .OUT

// while(true) {
//     ledGpio.value = 1
//     sleep(1)
//     ledGpio.value = 0
//     sleep(1)
// }





// I2C test---success
// import Foundation
// // public static let ADC: [Int: chn] = [
// //         0: i2ctest(0x40),
// //         1: i2ctest(0x41),
// //         2: i2ctest(0x42),
// //         3: i2ctest(0x43)
// //     ]
// while (true){
//     let i2ctest = SysFSI2C(i2cId:1)
//     i2ctest.writeByte(0x48, value: 0x41)
//     // i2ctest.readByte(0x48)
//     let result = i2ctest.readByte(0x48)
//     print(result)
// }



// ADC test

// import Foundation

// while true {
//     // let ADC  = ADCChn("A1")
    
//     let adc  = ADC("A0")
//     adc.choose()
//     // try! print(ADC.read())
//     sleep(1)
// }



// PWM test
/*
import Foundation

// _ (void)delayMethod
// {
//     NSLog(@"delayMethodEnd = %@",[NSThread currentThread]);
// }

let pwm = PWM(1)
pwm.period(1000)
pwm.prescaler(10)
// pwm.pulse_width(31)
// pwm.pulse_width(16)
// pwm.pulse_width(4095)
// pwm.pulse_width(777)//pass
// pwm.pulse_width(1777)//pass
// pwm.pulse_width(100)
// pwm.pulse_width(666)
// pwm.pulse_width(1777)//flase
// pwm.pulse_width(777)//flase
// pwm.pulse_width(68)//flase
// pwm.pulse_width(2048)//flase
// pwm.pulse_width(2040)//flase
while true{
    for i in 0...4095{
        // DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            
        //     print("i:\(i)")
        //     pwm.pulse_width(i)
        //     print("iii:\(i)")

        // }
        // DispatchQueue.main.asyncAfter(deadline: .now() + .milliseconds(100)) {
        //     print("i:\(i)")
        //     pwm.pulse_width(i)
        //     print("iii:\(i)")
        // }
        pwm.pulse_width(i)
        print("i:\(i)")
            // NSTimer *timer = [NSTimer scheduledTimerWithTimeInterval:0.5 target:self selector:@selector(delayMethod) userInfo:nil repeats:NO];
            // [NSThread sleepForTimeInterval:2.0];
    }
}  


    // p = PWM(5)
    // # p.debug = 'debug'
    // p.period(1000)
    // p.prescaler(10)
    // # p.pulse_width(2048)
    // while True:
    //     for i in range(0, 4095, 10):
    //         p.pulse_width(i)
    //         print(i)
    //         time.sleep(1/4095)
    //     time.sleep(1)
    //     for i in range(4095, 0, -10):
    //         p.pulse_width(i)
    //         print(i)
    //         time.sleep(1/4095)
    //     time.sleep(1)

// func testI2c()  {
//     SysFSPWM.writeByte(ADDR, value: UInt8(CCR_l))
//     SysFSPWM.writeByte(ADDR, value: UInt8(CCR_h))
// }

// https://blog.csdn.net/potato512/article/details/70306226


*/

//Jelly test

import Foundation

func teat()  {
    while true{
        print ("######################################")
        print ("#                                    #")
        print ("#             Test Jelly             #")
        print ("#                                    #")
        print ("#  1. Read               8. LED      #")
        print ("#  2. Write              9. RGB      #")
        print ("#  3. Button             10. LEDBar  #")
        print ("#  4. Slider             11. Buzzer  #")
        print ("#  5. Sound Sensor       12. Motor   #")
        print ("#  6. Light Sensor       13. Servo   #")
        print ("#  7. Distance Sensor                #")
        print ("#                                    #")
        print ("#        [1,3,4,5,6,7,]---A0         #")
        print ("#     [2,8,9,10,11,12,13]---P0       #")
        print ("######################################")
        print("")
        let input =  readLine()?.split(separator: " ")
        let choice = Intinput!
        guard (choice > 13 || choice < 1) else {
            print("Please one above")
            continue
        }
        if choice == 1{
            let obj = Jelly_IN(0)
            func _test()  {
                let time: TimeInterval = 1.0/4095.0
                DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                print(obj.read())
                }
            }
        }
        else if choice == 2{
            let obj = Jelly(0)
            func _test()  {
                for i in stride(from: 0, to: 4095, by: 10){
                    let time: TimeInterval = 1.0/4095.0
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    print(obj.write(i))
                    }
                }
                sleep(1)
                for i in stride(from: 4095, to: 0, by: -10){
                    let time: TimeInterval = 1.0/4095.0
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    print(obj.write(i))
                    }
                }
                sleep(1)
            }
        }
        else if choice == 3{
            let obj = Button(0)
            func _test()  {
                let time: TimeInterval = 1.0/4095.0
                DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                print(obj.read())
                }
            }
            }
        else if choice == 4{
            let obj = Slider(0)
            func _test()  {
                let time: TimeInterval = 1.0/4095.0
                DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                print(obj.read())
                }
            }
        }
        else if choice == 5{
            let obj = SoundSensor(0)
            func _test()  {
                let time: TimeInterval = 1.0/4095.0
                DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                print(obj.read())
                }
            }
        }
        else if choice == 6{
            let obj = LightSensor(0)
            func _test()  {
                let time: TimeInterval = 1.0/4095.0
                DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                print(obj.read())
                }
            }
        }
        else if choice == 7{
            let obj = DistanceSensor(0)
            func _test()  {
                let time: TimeInterval = 1.0/4095.0
                DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                print(obj.read())
                }
            }
        }
        else if choice == 8{
            let obj = LED(0)
            func _test()  {
                for i in stride(from: 0, to: 4095, by: 10){
                    let time: TimeInterval = 1.0/4095.0
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    print(obj.write(i))
                    }
                }
                sleep(1)
                for i in stride(from: 4095, to: 0, by: -10){
                    let time: TimeInterval = 1.0/4095.0
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    print(obj.write(i))
                    }
                }
                sleep(1)
            }
        }
        else if choice == 9{
            let obj = RGB(0)
            func _test() {
                obj.color(0x00FF00)
            }
        }
        else if choice == 10{
            let obj = LEDBar(0)
            func _test()  {
                for i in stride(from: 0, to: 4095, by: 10){
                    let time: TimeInterval = 1.0/4095.0
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    print(obj.write(i))
                    }
                }
                sleep(1)
                for i in stride(from: 4095, to: 0, by: -10){
                    let time: TimeInterval = 1.0/4095.0
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    print(obj.write(i))
                    }
                }
                sleep(1)
            }
        }
        else if choice == 11{
            let obj = Buzzer(0)
        }
        else if choice == 12{
            let obj = Motor(0)
            func _test()  {
                obj.speed(-4095)
                print(-4095)
                obj.speed(4095)
                print(4095)
            }
        }
        else if choice == 13{
            let obj = Servo(0)
            func _test() {
                for i in stride(from: 0, to: 180, by: 1){
                    let time: TimeInterval = 0.01
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    obj.angle(i)
                    }     
                }
                sleep(1)
                for i in stride(from: 180, to: 0, by: -1){
                    let time: TimeInterval = 0.01
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
                    print(i)
                    obj.angle(i)
                    }     
                }
                sleep(1)
            }
        }

        // let read_arr = [1,3,4,5,6,7]
        // let write_arr = [2, 8, 10]
        // if read_arr.contains(choice){
        //     func _test()  {
        //         let time: TimeInterval = 1.0/4095.0
        //         DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
        //         print(obj.read())
        //         }
        //     }

        // }
        // else if write_arr.contains(choice){
        //     func _test()  {
        //         for i in stride(from: 0, to: 4095, by: 10){
        //             let time: TimeInterval = 1.0/4095.0
        //             DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
        //             print(i)
        //             print(obj.write(i))
        //             }
        //         }
        //         sleep(1)
        //         for i in stride(from: 4095, to: 0, by: -10){
        //             let time: TimeInterval = 1.0/4095.0
        //             DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
        //             print(i)
        //             print(obj.write(i))
        //             }
        //         }
        //         sleep(1)
        //     }
        // }

        // else if choice == 12{
        //     func _test()  {
        //         obj.speed(-4095)
        //         print(-4095)
        //         obj.speed(4095)
        //         print(4095)
        //     }
        // }
        // else if choice == 9 {
        //     func _test() {
        //         obj.color(0x00FF00)
        //     }
        // }
        // else if choice == 13{
        //     func _test() {
        //         for i in stride(from: 0, to: 180, by: 1){
        //             let time: TimeInterval = 0.01
        //             DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
        //             print(i)
        //             obj.angle(i)
        //             }     
        //         }
        //         sleep(1)
        //         for i in stride(from: 180, to: 0, by: -1){
        //             let time: TimeInterval = 0.01
        //             DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + time) { 
        //             print(i)
        //             obj.angle(i)
        //             }     
        //         }
        //         sleep(1)
        //     }
        // }
        while true{
            try? _test()
        }
        
    }

}

