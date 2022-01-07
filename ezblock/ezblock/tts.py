from io import SEEK_END
from ssl import RAND_pseudo_bytes
from .basic import _Basic_class
from .utils import log
from .music import Music
from distutils.spawn import find_executable
import json

class TTS(_Basic_class):
    _class_name = 'TTS'
    SUPPORTED_LANGUAUE = [
        'zh-CN', # 普通话(中国)
        'en-US', # 英语(美国)English-United States
        'en-GB', # 英语(英国)English-United Kingdom
        'de-DE', # 德语(德国)Germany-Deutsch
        'es-ES', # 西班牙语(西班牙)España-Español
        'fr-FR', #  法语(法国)France-Le français
        'it-IT', # 意大利语(意大利)Italia-lingua italiana
    ]

    def __init__(self, data):
        super().__init__()
        if  isinstance(data, dict) is not True:
            from .websockets import Ezb_Service
            Ezb_Service().set_share_val('debug', "data parameter is incorrect")
            raise ValueError('data parameter is incorrect')
        try: 
            self._lang = "en-US"            # 默认语言:英语 default language:English
            self.engine = data['engine']
            self.url = data['url'] 
            self.token = data['token'] 
            if self.engine == "espeak":
                self._amp   = 100 
                self._speed = 175
                self._gap   = 5
                self._pitch = 50
            elif self.engine == "gtts" or self.engine == "polly":
                # import urllib.request as request
                import requests
                import base64
                # self.request = request
                self.requests = requests
                self.base64 = base64
        except Exception as e:
            from .websockets import Ezb_Service
            Ezb_Service().set_share_val('debug', "%s"%e)
            raise (e)

    def _check_executable(self, executable):
        executable_path = find_executable(executable)
        found = executable_path is not None
        return found

    def say(self, words:str):           # 输入的文字 
        if  words.strip() == '':
            from .websockets import Ezb_Service
            Ezb_Service().set_share_val('debug', "tts.say is missing parameters")
            log("tts.say is missing parameters")
        eval(f"self.{self.engine}(words)")

    def espeak(self, words):
        self._debug('espeak:\n [%s]' % (words))
        if not self._check_executable('espeak'):
            self._debug('espeak is busy. Pass')

        cmd = 'espeak -a%d -s%d -g%d -p%d \"%s\" --stdout | aplay 2>/dev/null & ' % (self._amp, self._speed, self._gap, self._pitch, words)
        self.run_command(cmd)
        self._debug('command: %s' %cmd)

    def gtts(self, words):
        sound_file = "/opt/ezblock/output.mp3"
        data = {
            "text": words,
            "language": self.lang(),
        }
        header = {
            "Content-Type": "application/json",
        }

        data =json.dumps(data)
        data = bytes(data, 'utf8')
        req = self.requests.Request(self.url, data=data, headers=header, method='POST')
        r = self.requests.urlopen(req)
        result = r.read()
        result = result.decode("utf-8")
        result = self.ast.literal_eval(result)
        data = result["data"]
        data = self.base64.b64decode(data)
        # print(data)
        with open(sound_file, "wb") as f:
            f.write(data)

        music = Music()
        music.sound_play(sound_file)


    def polly(self, words):
        sound_file = "/opt/ezblock/output.mp3"
        send_data = {
            "text": words,
            "language": self._lang,
            "token": self.token
        }
        header = {
            "Content-Type": "application/json",
        }
        # print(send_data)
        for i in range(5):
            r = self.requests.post(url=self.url, headers=header, json=send_data)
            result = r.json()
            # print('result: %s'%result)
            if result != "":
                break
            else:
                print("Empty result")
        else:
            raise IOError("Network Error")

        data = result["data"]
        # print(data)
        data = self.base64.b64decode(data)
        # print(data)
        with open(sound_file, "wb") as f:
            f.write(data)

        music = Music()
        music.sound_play(sound_file)

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

    def espeak_params(self, amp=None, speed=None, gap=None, pitch=None):
        if amp == None: 
            amp=self._amp
        if speed == None:
            speed=self._speed
        if gap == None:
            gap=self._gap
        if pitch == None:
            pitch=self._pitch

        if amp not in range(0, 200):
            raise ValueError('Amp should be in 0 to 200, not "{0}"'.format(amp))
        if speed not in range(80, 260):
            raise ValueError('speed should be in 80 to 260, not "{0}"'.format(speed))
        if pitch not in range(0, 99):
            raise ValueError('pitch should be in 0 to 99, not "{0}"'.format(pitch)) 
        self._amp   = amp
        self._speed = speed
        self._gap   = gap
        self._pitch = pitch
