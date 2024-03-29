#if os(Linux)
    import Glibc
#else
    import Darwin.C
#endif
import Foundation

internal let GPIOBASEPATH="/sys/class/gpio/"

// MARK: GPIO

public class GPIO {
    public var bounceTime: TimeInterval?

    public private(set) var name: String = ""
    public private(set) var id: Int = 0
    var exported = false
    var listening = false
    var intThread: Thread?
    var intFalling: (func: ((GPIO) -> Void), lastCall: Date?)?
    var intRaising: (func: ((GPIO) -> Void), lastCall: Date?)?
    var intChange: (func: ((GPIO) -> Void), lastCall: Date?)?

    public init(name: String, id: Int) {
        self.name = name
        self.id = id
    }

    public var direction: GPIODirection {
        set(dir) {
            if !exported {enableIO(id)}
            performSetting("gpio" + String(id) + "/direction", value: dir.rawValue)
        }
        get {
            if !exported { enableIO(id)}
            return GPIODirection(rawValue: getStringValue("gpio"+String(id)+"/direction")!)!
        }
    }

    public var edge: GPIOEdge {
        set(dir) {
            if !exported {enableIO(id)}
            performSetting("gpio"+String(id)+"/edge", value: dir.rawValue)
        }
        get {
            if !exported {enableIO(id)}
            return GPIOEdge(rawValue: getStringValue("gpio"+String(id)+"/edge")!)!
        }
    }

    public var activeLow: Bool {
        set(act) {
            if !exported {enableIO(id)}
            performSetting("gpio"+String(id)+"/active_low", value: act ? "1":"0")
        }
        get {
            if !exported {enableIO(id)}
            return getIntValue("gpio"+String(id)+"/active_low")==0
        }
    }

    public var pull: GPIOPull {
        set(dir) {
            fatalError("Unsupported parameter.")
        }
        get{
            fatalError("Parameter cannot be read.")
        }
    }

    public var value: Int {
        set(val) {
            if !exported {enableIO(id)}
            performSetting("gpio"+String(id)+"/value", value: val)
        }
        get {
            if !exported {enableIO(id)}
            return getIntValue("gpio"+String(id)+"/value")!
        }
    }

    public func isMemoryMapped() -> Bool {
        return false
    }

    public func onFalling(_ closure: @escaping (GPIO) -> Void) {
        intFalling = (func: closure, lastCall: nil)
        if intThread == nil {
            intThread = makeInterruptThread()
            listening = true
            intThread?.start()
        }
    }

    public func onRaising(_ closure: @escaping (GPIO) -> Void) {
        intRaising = (func: closure, lastCall: nil)
        if intThread == nil {
            intThread = makeInterruptThread()
            listening = true
            intThread?.start()
        }
    }

    public func onChange(_ closure: @escaping (GPIO) -> Void) {
        intChange = (func: closure, lastCall: nil)
        if intThread == nil {
            intThread = makeInterruptThread()
            listening = true
            intThread?.start()
        }
    }

    public func clearListeners() {
        (intFalling, intRaising, intChange) = (nil, nil, nil)
        listening = false
    }

}

fileprivate extension GPIO {

    func enableIO(_ id: Int) {
        writeToFile(GPIOBASEPATH+"export", value:String(id))
        exported = true
    }

    func performSetting(_ filename: String, value: String) {
        writeToFile(GPIOBASEPATH+filename, value:value)
    }

    func performSetting(_ filename: String, value: Int) {
        writeToFile(GPIOBASEPATH+filename, value: String(value))
    }

    func getStringValue(_ filename: String) -> String? {
        return readFromFile(GPIOBASEPATH+filename)
    }

    func getIntValue(_ filename: String) -> Int? {
        if let res = readFromFile(GPIOBASEPATH+filename) {
            return Int(res)
        }
        return nil
    }

    func writeToFile(_ path: String, value: String) {
        let fp = fopen(path, "w")
        if fp != nil {
          #if swift(>=3.2)
            let len = value.count
          #else
            let len = value.characters.count
          #endif
            let ret = fwrite(value, MemoryLayout<CChar>.stride, len, fp)
            if ret<len {
                if ferror(fp) != 0 {
                    perror("Error while writing to file")
                    abort()
                }
            }
            fclose(fp)
        }
    }

    func readFromFile(_ path: String) -> String? {
        let MAXLEN = 8

        let fp = fopen(path, "r")
        var res: String?
        if fp != nil {
            let buf = UnsafeMutablePointer<CChar>.allocate(capacity: MAXLEN)
            let len = fread(buf, MemoryLayout<CChar>.stride, MAXLEN, fp)
            if len < MAXLEN {
                if ferror(fp) != 0 {
                    perror("Error while reading from file")
                    abort()
                }
            }
            fclose(fp)
            //Remove the trailing \n
            buf[len-1]=0
            res = String.init(validatingUTF8: buf)
        #if swift(>=4.1)
            buf.deallocate()
        #else
            buf.deallocate(capacity: MAXLEN)
        #endif
        }
        return res
    }

    func makeInterruptThread() -> Thread? {
        //Ignored by Linux
        guard #available(iOS 10.0, macOS 10.12, *) else {return nil}

        let thread = Thread {

            let gpath = GPIOBASEPATH+"gpio"+String(self.id)+"/value"
            self.direction = .IN
            self.edge = .BOTH

            let fp = open(gpath, O_RDONLY)
            var buf: [Int8] = [0, 0, 0] //Dummy read to discard current value
            read(fp, &buf, 3)

          #if swift(>=4.0)
            var pfd = pollfd(fd:fp, events:Int16(truncatingIfNeeded:POLLPRI), revents:0)
          #else
            var pfd = pollfd(fd:fp, events:Int16(truncatingBitPattern:POLLPRI), revents:0)
          #endif
          
            while self.listening {
                let ready = poll(&pfd, 1, -1)
                if ready > -1 {
                    lseek(fp, 0, SEEK_SET)
                    read(fp, &buf, 2)
                    buf[1]=0

                    let res = String(validatingUTF8: buf)!
                    switch res {
                    case "0":
                        self.interrupt(type: &(self.intFalling))
                    case "1":
                        self.interrupt(type: &(self.intRaising))
                    default:
                        break
                    }
                    self.interrupt(type: &(self.intChange))
                }
            }
        }
        return thread
    }

    func interrupt(type: inout (func: ((GPIO) -> Void), lastCall: Date?)?) {
        guard let itype = type else {
            return
        }
        if let interval = self.bounceTime, let lastCall = itype.lastCall, Date().timeIntervalSince(lastCall) < interval {
            return
        }
        itype.func(self)
        type?.lastCall = Date()
    }
}

extension GPIO: CustomStringConvertible {
    public var description: String {
        return "\(name)<\(direction),\(edge),\(activeLow),\(pull)>: \(value)"
    }
}

// MARK: GPIO:Raspberry

public final class RaspberryGPIO: GPIO {

    var setGetId: UInt32 = 0
    var baseAddr: Int = 0
    var inited = false

    let BCM2708_PERI_BASE: Int
    let GPIO_BASE: Int

    var gpioBasePointer: UnsafeMutablePointer<UInt32>!
    var gpioGetPointer: UnsafeMutablePointer<UInt32>!
    var gpioSetPointer: UnsafeMutablePointer<UInt32>!
    var gpioClearPointer: UnsafeMutablePointer<UInt32>!

    public init(name: String, id: Int, baseAddr: Int) {
        self.setGetId = UInt32(1<<id)
        self.BCM2708_PERI_BASE = baseAddr
        self.GPIO_BASE = BCM2708_PERI_BASE + 0x200000 /* GPIO controller */
        super.init(name:name, id:id)
    }

    public override var value: Int {
        set(val) {
            if !inited {initIO()}
            gpioSet(val)
        }
        get {
            if !inited {initIO()}
            return gpioGet()
        }
    }

    public override var direction: GPIODirection {
        set(dir) {
            if !inited {initIO()}
            if dir == .IN {
                gpioAsInput()
            } else {
                gpioAsOutput()
            }
        }
        get {
            if !inited {initIO()}
            return gpioGetDirection()
        }
    }

    public override var pull: GPIOPull {
        set(pull) {
            if !exported {enableIO(id)}
            setGpioPull(pull)
        }
        get{
            fatalError("Parameter cannot be read.")
        }
    }

    public override func isMemoryMapped() -> Bool {
        return true
    }

    private func initIO() {
        var mem_fd: Int32 = 0

        //Try to open one of the mem devices
        for device in ["/dev/gpiomem", "/dev/mem"] {
            mem_fd=open(device, O_RDWR | O_SYNC)
            if mem_fd>0 {
                break
            }
        }
        guard mem_fd > 0 else {
            fatalError("Can't open /dev/mem , use sudo!")
        }

        let gpio_map = mmap(
            nil,                 //Any adddress in our space will do
            PAGE_SIZE,          //Map length
            PROT_READ|PROT_WRITE, // Enable reading & writting to mapped memory
            MAP_SHARED,          //Shared with other processes
            mem_fd,              //File to map
            off_t(GPIO_BASE)     //Offset to GPIO peripheral, i.e. GPFSEL0
            )!

        close(mem_fd)

        if (Int(bitPattern: gpio_map) == -1) {    //MAP_FAILED not available, but its value is (void*)-1
            perror("mmap error")
            abort()
        }
        gpioBasePointer = gpio_map.assumingMemoryBound(to: UInt32.self)

        gpioGetPointer = gpioBasePointer.advanced(by: 13)   // GPLEV0
        gpioSetPointer = gpioBasePointer.advanced(by: 7)    // GPSET0
        gpioClearPointer = gpioBasePointer.advanced(by: 10) // GPCLR0

        inited = true
    }

    private func gpioAsInput() {
        let ptr = gpioBasePointer.advanced(by: id/10)       // GPFSELn 0..5
        ptr.pointee &= ~(7<<((UInt32(id)%10)*3))                    // SEL=000 input
    }

    private func gpioAsOutput() {
        let ptr = gpioBasePointer.advanced(by: id/10)       // GPFSELn 0..5
        ptr.pointee &= ~(7<<((UInt32(id)%10)*3))
        ptr.pointee |=  (1<<((UInt32(id)%10)*3))                    // SEL=001 output
    }

    private func gpioGetDirection() -> GPIODirection {
        let ptr = gpioBasePointer.advanced(by: id/10)       // GPFSELn 0..5
        let d = (ptr.pointee & (7<<((UInt32(id)%10)*3)))
        return (d == 0) ? .IN : .OUT
    }

    func setGpioPull(_ value: GPIOPull){
        let gpioGPPUDPointer = gpioBasePointer.advanced(by: 37)
        gpioGPPUDPointer.pointee = value.rawValue   // Configure GPPUD
        usleep(10);                                 // 150 cycles or more
        let gpioGPPUDCLK0Pointer = gpioBasePointer.advanced(by: 38)
        gpioGPPUDCLK0Pointer.pointee = setGetId     // Configure GPPUDCLK0 for specific gpio (Ids always lower than 31, no GPPUDCLK1 needed)
        usleep(10);                                 // 150 cycles or more
        gpioGPPUDPointer.pointee = 0                // Reset GPPUD
        usleep(10);                                 // 150 cycles or more
        gpioGPPUDCLK0Pointer.pointee = 0            // Reset GPPUDCLK0/1 for specific gpio
        usleep(10);                                 // 150 cycles or more
    }

    private func gpioGet() -> Int {
        return ((gpioGetPointer.pointee & setGetId)>0) ? 1 : 0
    }

    private func gpioSet(_ value: Int) {
        let ptr = value==1 ? gpioSetPointer : gpioClearPointer
        ptr!.pointee = setGetId
    }

}

public struct SwiftyGPIO {

    public static func GPIOs() -> [GPIOName: GPIO] {
        return EzBlock
    }
}

// MARK: - Global Enums

public enum SupportedBoard {
    case RaspberryPiRev1   // Pi A,B Revision 1
    case RaspberryPiRev2   // Pi A,B Revision 2
    case RaspberryPiPlusZero // Pi A+,B+,Zero with 40 pin header
    case RaspberryPi2 // Pi 2 with 40 pin header
    case RaspberryPi3 // Pi 3 with 40 pin header
    case EzBlock
}

public enum GPIOName {
    case D0
    case D1
    case D2
    case D3
    case D4
    case D5
    case D6
    case D7
    case D8
    case D9
    case D10
    case D11
    case D12
    case D13
    case D14
    case D15
    case D16
    case SW
    case LED
    case PWR
    case RST
    case BLEINT
}

public enum GPIODirection: String {
    case IN="in"
    case OUT="out"
}

public enum GPIOEdge: String {
    case NONE="none"
    case RISING="rising"
    case FALLING="falling"
    case BOTH="both"
}

public enum GPIOPull: UInt32 {
    case neither = 0
    case down    = 1
    case up      = 2
}

public enum ByteOrder {
    case MSBFIRST
    case LSBFIRST
}

// MARK: - Constants

let PAGE_SIZE = (1 << 12)

// MARK: - Darwin / Xcode Support
#if os(OSX) || os(iOS)
    private var O_SYNC: CInt { fatalError("Linux only") }
#endif
