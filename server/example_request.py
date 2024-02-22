import requests, json
from pprint import pprint


url = 'http://127.0.0.1:8000/positions'

response = requests.get(url)

if response.status_code == 200:
    try:
        pprint(response.json())
    except ValueError:
        print("Response is not in JSON format.")
else:
    print("Error:", response.status_code, response.text)


url = 'http://127.0.0.1:8000/positions'
data = {"69": [1,1,1]}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, json=data, headers=headers)
print(response)