# Change Log

## [Unreleased]
...

## [1.2.3] - 2023-7-5

### Fixed
- Fix bug of Ezb_Service send "debug"


## [1.2.2] - 2023-5-26

### Optimized
- Compatible with different username, userhome


## [1.2.1] - 2022-11-30

### Added
- Add congfigure parameter of auto-start user block program in /opt/ezblock/ezb-info.ini
- Add Pake reference

### Changed
- Change tts engine to pico2wave. Note that the engine is offline and does not support Chinese
- Remove auto-start user block program
- Disable auto-start user block program

### Fixed
- Fix bug of spider calibration


## [1.2.0] - 2022-11-30

### Changed
- Change the update mechanism, increase the comparison of app version compatibility


## [1.1.4] - 2022-7-14 (Note that this version does not modify any code)

### Fixed
- System apt full-update, fix the problem that the new batch of Raspberry Pi can't use Bluetooth properly
  

## [1.1.3] - 2022-7-7

### Optimized
- Optimize the calibration of picar-x, picrawler, and pisloth
- Debug printing increased text color

### Fixed
- Fix the camera's ability to save high-resolution images


## [1.1.2] - 2022-6-13 - Official release

### Fixed
- Fix the IO conflict between ADC battery reading and ADC joystick

### Changed
- Change the address of update package detection and download


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
[1.2.2]: https://github.com/ezblockcode/ezb-pi/tree/1.2.2
[1.2.1]: https://github.com/ezblockcode/ezb-pi/tree/1.2.1
[1.2.0]: https://github.com/ezblockcode/ezb-pi/tree/1.2.0
[1.1.4]: https://github.com/ezblockcode/ezb-pi/tree/1.1.4
[1.1.3]: https://github.com/ezblockcode/ezb-pi/tree/1.1.3
[1.1.2]: https://github.com/ezblockcode/ezb-pi/tree/1.1.2
[1.1.1]: https://github.com/ezblockcode/ezb-pi/tree/1.1.1
[1.1.0]: https://github.com/ezblockcode/ezb-pi/tree/1.1.0
[1.0.5]: https://github.com/ezblockcode/ezb-pi/tree/1.0.5
[1.0.4]: https://github.com/ezblockcode/ezb-pi/tree/1.0.4
[1.1.0_Beta]: https://github.com/ezblockcode/ezb-pi/tree/1.1.0_Beta
[1.0.3]: https://github.com/ezblockcode/ezb-pi/tree/1.0.3
[1.0.2]: https://github.com/ezblockcode/ezb-pi/tree/1.0.2
