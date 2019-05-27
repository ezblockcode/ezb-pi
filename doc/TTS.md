# class TTS - text to speech

Usage:
```python
from ezblock import *

tts = TTS()                     # create an TTS object
tts.say('hello')                #write word

# tts.write('hi')                #write word
tts.lang('en-GB')                #change language

tts.supported_lang()            #return language
```
## Constructors
```class ezblock.TTS(pin)```
Create an TTS object.

## Methods
- say - Write word on TTS.
```python
TTS.say(words)
```
- lang - Change on TTS.
```python
TTS.lang(language)
```
- supported_lang - Inquire the language.
```python
TTS.supported_lang()
```