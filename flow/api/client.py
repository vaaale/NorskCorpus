import requests
import json

url = "http://localhost:5000/"

data = json.dumps({'sender': "Alexander Vaagan", "position": "AI God"})


fin = open('/home/alex/Downloads/2018-13 LN-PTS.pdf', 'rb')
files = {'file': fin}
try:
    r = requests.post(url, files=files, data={'data': data})
    print(r.text)
finally:
    fin.close()