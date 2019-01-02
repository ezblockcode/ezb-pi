import Foundation
// import Darwin


// public class PWM {

//     public var channel: String
//     // public var function1 = PWMChn(0x20)

//     public init(_ channel: String) {
//         self.channel = channel
//     }
    
//     public func choose() {
//         print("next1")
//         switch channel {
//             case "P1":
//                 var function1 = PWMChn(0x20)
//             case "P2":
//                 var function1 = PWMChn(0x21)
//             case "P3":
//                 var function1 = PWMChn(0x22)
//             case "P4":
//                 var function1 = PWMChn(0x23)
//             case "P5":
//                 var function1 = PWMChn(0x24)
//             case "P6":
//                 var function1 = PWMChn(0x25)
//             case "P7":
//                 var function1 = PWMChn(0x26)
//             case "P8":
//                 var function1 = PWMChn(0x27)
//             default:
//                 break
        
//         }
//     //     try! print(function.read())
//     // return function1
//     }
// }

public final class PWM {
    public let reg : Int = 0x20
    public let channel: Int
    public let ADDR: Int = 0x14
    var _freq: Int = 50
    let CLOCK: Int = 72000000
    let PRECISION: Int = 4095
    var _pulse_width: Int = 0
    let i2cId: Int = 1
    var _arr: Int = 4095
    let REG_PSC:Int = 0x28
    let REG_ARR:Int = 0x2A
    let i2c: SysFSI2C


    public init(_ channel: Int){
        i2c = SysFSI2C(i2cId:i2cId)
        self.channel = channel + 0x20
        freq(50)
    }
     
    public func i2c_write(reg:Int, value: Int) throws  {
        // print("next")

        let value_h = value >> 8
        print(value_h)
        let value_l = UInt8(value & 0x00ff)
        i2c.writeByte(0x14, value: UInt8(reg))
        i2c.writeByte(0x14, value: UInt8(value_h))
        i2c.writeByte(0x14, value: UInt8(value_l))
    }
   
    public func freq(_ freq: Int?) {
        var result_ap : Array<Array<Int>>
        result_ap = Array<Array<Int>>()
        var result_acy : Array<Int>
        result_acy = Array<Int>()
        var b: Int = 0
        if freq == nil {
            fatalError("freq cannot be nil")
        }
        else {
            _freq = freq!
            var st = Int(sqrt(Double(CLOCK/_freq)))
            st -= 5
            if  st <= 0{
                st = 1
            }

            for psc in st...(st+10){
                let arr = Int((Double(CLOCK)/Double(_freq))/Double(psc))
                result_ap.append([psc, arr])
                result_acy.append(Int(abs(Double(_freq-CLOCK)/Double(psc))/Double(arr)))
            }
            // Find the subscript of the minimum
            var n = result_acy[0]
            if result_acy.count == 1{
                b = 0
            }
            else{
                for i in 1..<(result_acy.count) {
                    if n > result_acy[i] {
                        n = result_acy[i]
                        b = i    
                    }
                }
            }
        let psc = result_ap[b][0]
        let arr = result_ap[b][0]
        prescaler(psc)
        period(arr)
        }
    }

    public func prescaler(_ prescaler: Int?) {
        if prescaler == nil {
            fatalError("prescaler cannot be nil")
        }
        else{
            let _prescaler = prescaler!
            try! i2c_write(reg: REG_PSC, value: Int(_prescaler))
        }
    }

    public func period(_ arr: Int?) {
        if arr == nil {
            fatalError("arr cannot be nil")
        }
        else{
            _arr = arr!
            try! i2c_write(reg:REG_ARR, value: Int(_arr))

        }
    }

    public func pulse_width(_ pulse_width: Int?) {
        if pulse_width == nil {
            fatalError("pulse_width")
        }
        else{
            _pulse_width = pulse_width!
            let CCR = Int((Double(_pulse_width)/Double(PRECISION)) * Double(_arr))
            print("CCR:\(CCR)")
            try! i2c_write(reg:channel, value: Int(CCR))

        }
    }
}  
// MARK: - Darwin / Xcode Support
#if os(OSX) || os(iOS)
    private var O_SYNC: CInt { fatalError("Linux only") }
#endif