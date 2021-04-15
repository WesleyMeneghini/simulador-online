import json
import requests
from src import acesso

def sendMessage(message, number):

    url = f'{acesso.getUrlApiWhats}'
    payload = {'message': f'{message}',
               'number': f'{number}'}
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'Authorization': f'{acesso.getAuthorization}'}

    return requests.post(url, data=json.dumps(payload), headers=headers)
