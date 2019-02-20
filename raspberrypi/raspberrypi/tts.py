from basic import _Basic_class
from distutils.spawn import find_executable

class TTS(_Basic_class):
    _class_name = 'TTS'

    def __init__(self, engine='pico'):
        super().__init__()
        self._lang = "en-US"

    def _check_executable(self, executable):
        executable_path = find_executable(executable)
        found = executable_path is not None
        return found

    def say(self, words):
        self.write(words)

    def write(self, words):
        self._debug('Say:\n [%s]' % (words))
        if self._check_executable('pico2wave') and self._check_executable('aplay'):
            cmd = 'pico2wave -l %s -w /tmp/pico.wav "%s" && aplay /tmp/pico.wav' % (self._lang, words)
            self.run_command(cmd)
            self._debug('command: %s' %cmd)
        else:
            self._debug('Festival is busy. Pass')

    @property
    def lang(self):
        return self._lang
    
    @lang.setter
    def lang(self, value):
        self.lang = value
