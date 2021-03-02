import requests
import json

def get():
    data = {
             "value": 200,
             "message": "success",
             "data": {
                "id": 8,
                "version": "1.5",
                "url": "https://test2.ezblock.com.cn/version/4.rar",
                "description": "hello",
                "creattime": "17"
                    }
            }
    headers={'Content-Type': 'application/json'}
    r = requests.post('https://test2.ezblock.com.cn:11000/api/web/v2/ezblock/get/last/version', json=data, headers=headers)
    result = r.content.decode('utf-8')
    result = json.loads(result)
    print(result['data']['version'])
    
get()
    