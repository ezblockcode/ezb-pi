# class SSD1306 - class for SSD1306-based OLED displays

Usage:
```python
from ezblock import SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
disp = SSD1306()
disp.begin()  # Initialize library.
disp.clear()  # Clear display.
disp.display()
width = disp.width  # Create blank image for drawing.
height = disp.height
image = Image.new('1', (width, height))  # Make sure to create image with mode '1' for 1-bit color.
draw = ImageDraw.Draw(image)  # Get drawing object to draw on image.
draw.rectangle((0,0,width,height), outline=0, fill=0)  # Draw a black filled box to clear the image.
font = ImageFont.load_default()  # Load default font.
draw.text((0, 0),    'Hello',  font=font, fill=255)  # Write two lines of text.
draw.text((2, 20), 'World!', font=font, fill=255)
disp.image(image)  # Display image.
disp.display()
```

## Constructors
```class ezblock.SSD1306()```
Create an OLED displays object.This screen size is 128x64

## Methods
- write_command - Send command byte to display
```python
SSD1306.write_command(c)
```
- write_data - Send byte of data to display
```python
SSD1306.write_data(c)
```
- begin - Initialize display
```python
SSD1306.begin()
```
- display - Write display buffer to physical display
```python
SSD1306.display()
```
- image - Set buffer to value of Python Imaging Library image.  The image should be in 1 bit mode and a size equal to the display size
```python
SSD1306.image(image)
```
- clear - Clear contents of image buffer
```python
SSD1306.clear()
```
- set_contrast - Sets the contrast of the display.  Contrast should be a value between 0 and 255
```python
SSD1306.set_contrast(contrast)
```
- dim - Adjusts contrast to dim the display if dim is True, otherwise sets the contrast to normal brightness if dim is False
```python
SSD1306.dim(dim)
```

