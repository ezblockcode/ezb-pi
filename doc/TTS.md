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
```class ezblock.TTS(engine)```
Create an TTS object. engine could be `"espeak"` as Espeak, `"gtts"` as Google TTS and `polly` as AWS Polly

## Methods
- say - Write word on TTS.
```python
TTS.say(words)
```
- lang - Change on TTS.
```python
TTS.lang(language)
```
- supported_lang - Inquire all supported language.
```python
TTS.supported_lang()
```