## Ezblock for Raspberry Pi
Ezblock for **RaspberryPi 3B+**, compatible for **Rev 4 Module B**

Quick Links:

 * [About Ezblock](#about_this_kit)
 * [Doc](#doc)
 * [Update](#update)
 * [About SunFounder](#about_sunfounder)
 * [License](#license)
 * [Contact us](#contact_us)

<a id="about_this_kit"></a>
### About Ezblock:
This is a img with whole bunch of sensors and activaters, provided by SunFounder. If any error or BUGs, wellcom to post issus in Github, or [Email](#contact_us) us.


<a id="doc"></a>
### Doc:
https://github.com/sunfounder-ezblock/ezb-pi/tree/master/doc


<a id="update"></a>
### Update:
https://github.com/ezblockcode/ezb-pi/blob/EzBlock3.1/CHANGELOG.md


### Usage
Trun on ezblock service:
```bash
sudo update-rc.d ezblock defaults
sudo update-rc.d ezblock-reset defaults
```
Trun off ezblock service:
```bash
sudo update-rc.d ezblock remove
sudo update-rc.d ezblock-reset remove
```

### Trouble Shooting
1. log prompt: `sudo: /usr/bin/ezblock-reset-service: No such file or directory`
    Maybe the problem of line ending of `ezblock-reset-service`, change it from CRLF to LF, and try again.

----------------------------------------------
<a id="about_sunfounder"></a>
### About SunFounder
SunFounder is a technology company focused on Raspberry Pi and Arduino open source community development. Committed to the promotion of open source culture, we strives to bring the fun of electronics making to people all around the world and enable everyone to be a maker. Our products include learning kits, development boards, robots, sensor modules and development tools. In addition to high quality products, SunFounder also offers video tutorials to help you make your own project. If you have interest in open source or making something cool, welcome to join us!

----------------------------------------------
<a id="license"></a>
### License
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied wa rranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

{Repository Name} comes with ABSOLUTELY NO WARRANTY; for details run ./show w. This is free software, and you are welcome to redistribute it under certain conditions; run ./show c for details.

SunFounder, Inc., hereby disclaims all copyright interest in the program '{Repository Name}' (which makes passes at compilers).

Mike Huang, 21 August 2015

Mike Huang, Chief Executive Officer

Email: service@sunfounder.com, support@sunfounder.com

----------------------------------------------
<a id="contact_us"></a>
### Contact us:
website:
    www.sunfounder.com

E-mail:
    service@sunfounder.com, support@sunfounder.com
