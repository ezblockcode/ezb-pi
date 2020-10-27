# class Buzzer - passive buzzer
Usage:
```python
from ezblock import PWM, Buzzer, Music

pwm = PWM("A0")                 # create pwm object
buzzer = Buzzer(pwm)            # create an Buzzer object with PWM object
music = Music()                 # create music object

buzzer.play(music.note("Low C"), music.beat(1))   # play low C for 1 beat
buzzer.play(music.note("Middle C#"))              # play middle C sharp
buzzer.off()                                      # turn buzzer off
```
## Constructors
```class ezblock.Buzzer(pwm)```
Create an Buzzer object associated with the given pwm object. This allows you to then control buzzer.

## Methods
- `on` - Turn the buzzer on with a square wave
```python
Buzzer.on()
```
- `off` - Turn the buzzer off 
```python
Buzzer.off()
```
- `freq` - Set the square wave frequency 
```python
Buzzer.freq(frequency)
```
- `play` - Play freq, set off if a ms delay arguement is provided. 
```python
Buzzer.play(freq, ms)
Buzzer.play(freq)
```
