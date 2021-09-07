import urllib.request as request
import base64
import ast, json

LANGS = [
    "zh-CN",
    "en-US",
]

data = {
    "text": "你好",
    "language": LANGS[0],
}
header = {
    "Content-Type": "application/json",
}

data = json.dumps(data)
data = bytes(data, 'utf8')
url = 'http://192.168.6.224:11000/api/web/v2/ezblock/google/tts'
req = request.Request(url, data=data, headers=header, method='POST')
r = request.urlopen(req)
result = r.read()
result = result.decode("utf-8")
result = ast.literal_eval(result)
data = result["data"]
data = base64.b64decode(data)
print(data)
with open("output.mp3", "wb") as f:
    f.write(data)
