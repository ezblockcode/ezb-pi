
// #if os(Linux)
//     import Glibc
// #else
//     import Darwin.C
// #endif
  
import Foundation

// enum ADCError: Error {
//     case fileError
//     case readError
//     case conversionError
// }

// extension SwiftyGPIO {

//     public static func hardwareADCs() -> [ADCInterface]? {
//         // return [ADCBBB[0]!, ADCBBB[1]!, ADCBBB[2]!, ADCBBB[3]!]
//         return [ADCBBB[0]!, ADCBBB[1]!, ADCBBB[2]!, ADCBBB[3]!, ADCBBB[4]!, ADCBBB[5]!, ADCBBB[6]!, ADCBBB[7]!]
//     }
// }

// MARK: - ADC chn



public class ADC {

    public var chnnal: String
    public var function = ADCChn(0x17)

    public init(_ chnnal: String) {
        self.chnnal = chnnal
    }
    
    public func choose()  {

        switch chnnal {
            case "A0":
                function = ADCChn(0x17)
            case "A1":
                function = ADCChn(0x16)
            case "A2":
                function = ADCChn(0x15)
            case "A3":
                function = ADCChn(0x14)
            case "A4":
                function = ADCChn(0x13)
            case "A5":
                function = ADCChn(0x12)
            case "A6":
                function = ADCChn(0x11)
            case "A7":
                function = ADCChn(0x10)
            default:
                break
        
        }
        try! print(function.read())
    }
}

// extension SwiftyGPIO {

// public final class func hardwareADCs() -> [ADCInterface]? {
    
//     return [ADC[0]!, ADC[1]!, ADC[2]!, ADC[3]!, ADC[4]!, ADC[5]!, ADC[6]!, ADC[7]!]
// }
// // }

// // extension SwiftyGPIO {
// public final class let ADC: [Int: ADCInterface] = [
//     0: ADCChn(0x17),
//     1: ADCChn(0x16),
//     2: ADCChn(0x15),
//     3: ADCChn(0x14),
//     4: ADCChn(0x13),
//     5: ADCChn(0x12),
//     6: ADCChn(0x11),
//     7: ADCChn(0x10)
// ]
// // }

// public protocol ADCInterface {
//         var chn: Int { get }
//         func read() throws -> Int 
// }

/// ADC 
public final class ADCChn {
    public var chn: Int
    public let i2cId: Int = 1

    public init(_ chn: Int) {
        // self.chn = Int(chn,radix:16)
        if (chn >= 0 && chn < 4) {
            self.chn = 0x17 - chn
        }
        else{
            self.chn = chn     
        }
        
    }
    // let chn_int = Int(String(chn,radix:16))!
    // self.chn = chn_int
    // print("chn0-2:\(chn)")  
    // chnn = Int(chn,radix:16)   

    public func read() throws -> Int {
        let ADDR:Int = 0x14
        let recv = 1
        var data_all : Array<UInt8>
        var d: UInt8
        // var j: UInt8 = 0
        // switch chn {
        //     case "A0":
        //         chnn = 0x
        // }
        data_all = Array<UInt8>()
        for j in 0...100{
            d = UInt8(chn) >> (8*UInt8(j)) & 0xFF
            // j = j + 1
            if d == UInt8(0) {
                break
            }
            else{
                data_all.append(d)
            }
        }
        let len = data_all.count

        var data_reverse : Array<UInt8>
        data_reverse = Array<UInt8>()
        if len == 1{
            data_reverse.append(data_all[0])
        
        }
        else if len > 1{
            for j in 0...(len-1) {
                data_reverse.append(data_all[len-1-j])
            }
        }
        // // chnn = Int(chn,radix:16)
        // let chnn = Int(chn, radix:16)     
        switch len {
            case 0:
                let SysFSADC = SysFSI2C(i2cId: i2cId)
                SysFSADC.writeQuick(chn)
            case 1:
                // let data = data_reverse[0]
                // print("4:\(data)")
                let SysFSADC = SysFSI2C(i2cId:i2cId)
                print("chn:\(chn)")
                // print("data:\(data)")
                // print("ADDR:\(ADDR)")
                SysFSADC.writeByte(0x14, value: UInt8(22))//0x14 Cannot be assigned by parameter
            case 2:
                let reg = data_reverse[0]
                let data = data_reverse[1]
                let SysFSADC = SysFSI2C(i2cId:i2cId)
                SysFSADC.writeByte(chn, command: reg, value: data) 
            case 3:
                let reg = data_reverse[0]
                let data: UInt16 = UInt16(data_reverse[1])
                let SysFSADC = SysFSI2C(i2cId:i2cId)
                SysFSADC.writeWord(chn, command: reg, value: data)
            default:
                let reg = data_reverse[0]
                let data = [UInt8](data_reverse.dropFirst())
                let SysFSADC = SysFSI2C(i2cId:i2cId)
                SysFSADC.writeData(chn, command: reg, values:data)
                
        } 
        // var b:[Byte] = [13,0xf1,0x20]
        // var d = NSData(bytes: b, length: 3)
        
        // var byteArray:[Byte] = [Byte]()
        // for i in 0..<3 {
        //     var temp:Byte = 0
        //     d.getBytes(&temp, range: NSRange(location: i,length:1 ))
        //     byteArray.append(temp)
        // }



        // var recv_array = [recv]
        // recv_array[0] = recv

        let bytearray: [UInt8] = [UInt8(recv)]
        let byteArray = NSData(bytes: bytearray, length: bytearray.count)

        // var foo:[UInt8] = [0xff, 0xD9]
        // var data = NSData(bytes: foo, length: foo.count)

        // d.getBytes(&temp, range: NSRange(location: 0,length:1 ))
        // byteArray.append(temp)
        let SysFSADC = SysFSI2C(i2cId:i2cId)
        let value_h = byteArray
        var value_high: Array<Int>
        value_high = Array<Int>()
        let h_len = value_h.length
        // print(h_len)
        if h_len == 1{
            let high_h = SysFSADC.readByte(0x14)
            value_high.append(Int(high_h))
        }
        
        else if h_len > 1{
            for _ in 0...(h_len-1) {
                let high_h = SysFSADC.readByte(chn, command: 0)
                value_high.append(Int(high_h))
            }
        }
        let value_l = byteArray
        var value_low : Array<Int>
        value_low = Array<Int>()
        let l_len = value_l.length
        if l_len == 1{
            let high_1 = SysFSADC.readByte(0x14)
            value_low.append(Int(high_1))
        }
        else if l_len > 1{
            for _ in 0...(l_len-1) {
                let high_1 = SysFSADC.readByte(chn, command: 0)
                value_low.append(Int(high_1))
            }
        }
        print("value_high[0]:\(value_high[0])")
        print("value_low[0]:\(value_low[0])")
        let value = (value_high[0] << 8) + value_low[0]
        print("value:\(value)")
        return value
    }
}

// MARK: - Darwin / Xcode Support
#if os(OSX) || os(iOS)
    private var O_SYNC: CInt { fatalError("Linux only") }
#endif





