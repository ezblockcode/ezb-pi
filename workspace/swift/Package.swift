import PackageDescription
let package = Package(
    name: "led-blink",
    dependencies: [
        .Package(url: "https://github.com/uraimo/SwiftyGPIO.git", majorVersion: 0),
        .Package(url: "./Source/libs/pin.swift"),
    ]
)
