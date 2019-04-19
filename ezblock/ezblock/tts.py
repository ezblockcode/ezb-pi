from ezblock.basic import _Basic_class
from distutils.spawn import find_executable

class TTS(_Basic_class):
    _class_name = 'TTS'
    SUPPORTED_LANGUAUE = [
        'en-US', #英语(美国)English-United States
        'en-GB', # 英语(英国)English-United Kingdom
        'de-DE', # 德语(德国)Germany-Deutsch
        'es-ES', # 西班牙语(西班牙)España-Español
        'fr-FR', #  法语(法国)France-Le français
        'it-IT', # 意大利语(意大利)Italia-lingua italiana
    ]

    def __init__(self, engine='pico'):
        super().__init__()
        self._lang = "en-US"            # 默认输入的语言为英语

    def _check_executable(self, executable):
        executable_path = find_executable(executable)
        found = executable_path is not None
        return found

    def say(self, words):           # 输入的文字
        self.write(words)

    def write(self, words):
        self._debug('Say:\n [%s]' % (words))
        if self._check_executable('pico2wave') and self._check_executable('aplay'):
            cmd = 'pico2wave -l %s -w /tmp/pico.wav "%s" && aplay /tmp/pico.wav' % (self._lang, words)  # 传入语言，和需要转换成语言的文字
            self.run_command(cmd)
            self._debug('command: %s' %cmd)
        else:
            self._debug('pico is busy. Pass')

    def lang(self, *value):     # 切换语言，可识别5种语言
        if len(value) == 0:
            return self._lang
        elif len(value) == 1:
            v = value[0]
            if v in self.SUPPORTED_LANGUAUE:
                self._lang = v
                return self._lang
        raise ValueError("Arguement \"%s\" is not supported. run tts.supported_lang to get supported language type."%value)

    def supported_lang(self):           # 返回支持的语言类型
        return self.SUPPORTED_LANGUAUE

def test():
    tts = TTS()
    tts.lang("de-DE")
    tts.say("Wer bin ich")


if __name__ == "__main__":
    test()