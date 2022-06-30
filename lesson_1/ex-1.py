import json
from pathlib import Path
from pprint import pprint
import requests

# set username
user = 'pixijs'
# ask for an username if it is not set
if not user:
    user = input('Enter username: ')

# infinite loop while username is invalid
while True:
    url = f'https://api.github.com/users/{user}'
    try:
        response = requests.get(url)
        if response.ok:
            j_response = response.json()
            repos_url = j_response['repos_url']
            break
        else:
            print('Too many requests. Try again later.')
            exit(1)
    except Exception:
        user = input('Wrong username! Try again!\nEnter username: ')

repos_response = dict()
repos_response[user] = requests.get(repos_url).json()

# save repos_response in *.json file
file = f'{__file__.split("/")[-1].split(".")[0]}.json'
with open(file, 'w', encoding='utf-8') as out:
    json.dump(repos_response, out, indent=4, ensure_ascii=False)

repos = {user: []}
repos[user].append(
    {repo['name']: repo['svn_url'] for repo in repos_response[user]}
)

pprint(repos)
