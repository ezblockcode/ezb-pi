# Change Log 

## [Unreleased]


## [1.1.1] - 2022-5-31  - based on 1.1.0 
### Fixed
- Fix bug of speed limit of picar-x 

### Changed
- Remove the limitation of connecting multiple devices at the same time


## [1.1.0] - 2022-3-10 - based on 1.1.0_Beta - Unreleased

### Fixed
- Fix some bugs of some sensor modules
- Fix som bugs of product initialization

### Changed
- To avoid conflicts with sunfounder-controller, change the websocket port to 7852


### Added
- Add only one device is allowed to connect at the same time,
- Add bluetooth advertisement  will be turned off when connecting to websockets


## [1.0.5] - 2022-2-15 - based on 1.0.4

### Fixed
- Fix some bugs of piarm


## [1.0.4] - 2022-2-8 - based on 1.0.3

### Added
- Add servos limit for spider

### Fixed
- Fix some bugs of spider


## [1.1.0_Beta] - 2022-1-7

### Changed
- Use Raspberry Pi's onboard Bluetooth to communicate 
  with the app 
- Some changes related to app interaction

### Added
- Add connection status sound effect and LED indicator
- Add Bluetooth name and hosstname modification function
- Add log dividing line 
- Add servo limit for Picrawler 

### Fixed
- Fix data blocking in remote control
- Fix bugs for piarm

## [1.0.3] - 2021-11-29

### Added
- Install lsof tool 
- Add change log
- Add servo limit for Piarm 
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


[Unreleased]: https://github.com/ezblockcode/ezb-pi/tree/EzBlock3.1
[1.1.1]: https://github.com/ezblockcode/ezb-pi/tree/1.1.1
[1.1.0]: https://github.com/ezblockcode/ezb-pi/tree/1.1.0
[1.0.5]: https://github.com/ezblockcode/ezb-pi/tree/1.0.5
[1.0.4]: https://github.com/ezblockcode/ezb-pi/tree/1.0.4
[1.1.0_Beta]: https://github.com/ezblockcode/ezb-pi/tree/1.1.0_Beta
[1.0.3]: https://github.com/ezblockcode/ezb-pi/tree/1.0.3
[1.0.2]: https://github.com/ezblockcode/ezb-pi/tree/1.0.2
