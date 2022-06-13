# Change Log 

## [Unreleased]

## [1.0.8] - 2022-6-13 - based on 1.0.6

### Fixed
- Fixed the IO conflict between ADC battery reading and ADC joystick

### Optinized
- some optimizations 


## [1.0.7] - 2022-4-12 - based on 1.0.6

### Fixed
- Replaced the startup file in the /boot directory, to fixed the problem that 
the new batch of Raspberry Pi could not be started


## [1.0.6] - 2022-3-9 - based on 1.0.5

### Fixed
- Fix some bugs of some sensor modules


## [1.0.5] - 2022-2-15 - based on 1.0.4

### Fixed
- Fix some bugs of piarm


## [1.0.4] - 2022-2-8 - based on 1.0.3

### Added
- Add servos limit for spider

### Fixed
- Fix some bugs of spider

## [1.0.3] - 2021-11-29

### Added
- Install lsof tool 
- Add change log
- Add servo limit for piarm 
- Add step memory function for piarm
- Add battery display 
- Add websockets connection status 

### Fixed
- Fix data blocking in remote control
- Fix high CPU usage
- Fix websocket service failure when replacing wifi
- Fix the issue of OSError occasionally when disconnected
- Fix the issue of version update failure
- Fix Remote I/O error caused by power reading
- Fix conflicts between heartbeat and remote control 
- Fix checking update causing program blockage
- Fix calibration failure of PaKe products

### Changed
- Change TTS engine parameter

### Optimized
- Optimize log output
- Optimize code readability


## [1.0.2] - 2021-09-07
    - 


[Unreleased]: https://github.com/ezblockcode/ezb-pi/tree/EzBlock3.0
[1.0.8]: https://github.com/ezblockcode/ezb-pi/tree/1.0.8
[1.0.7]: https://github.com/ezblockcode/ezb-pi/tree/1.0.7
[1.0.6]: https://github.com/ezblockcode/ezb-pi/tree/1.0.6
[1.0.5]: https://github.com/ezblockcode/ezb-pi/tree/1.0.5
[1.0.4]: https://github.com/ezblockcode/ezb-pi/tree/1.0.4
[1.0.3]: https://github.com/ezblockcode/ezb-pi/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/ezblockcode/ezb-pi/compare/1.0.1...1.0.2
