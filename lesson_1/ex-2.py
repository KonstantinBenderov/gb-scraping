import json
import os
from pprint import pprint

import requests

access_token = os.getenv('ACCESS_TOKEN')
url = 'https://api.vk.com/method/users.get'
params = {
    'user_id': '1',
    'v': '5.131',
    'access_token': access_token
}

response = requests.get(url, params=params)
j_response = response.json()

file = f'{__file__.split("/")[-1].split(".")[0]}.json'
with open(file, 'w', encoding='utf-8') as out:
    json.dump(j_response, out, indent=4, ensure_ascii=False)

pprint(j_response)
