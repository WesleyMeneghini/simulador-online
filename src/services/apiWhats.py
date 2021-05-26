import json
import requests
from src import acesso

ativarEnvio = True
ativarLog = True

def sendMessage(message, number):

    url = f'{acesso.getUrlApiWhats}'
    payload = {'message': f'{message}',
               'number': f'{number}'}
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'Authorization': f'{acesso.getAuthorization}'}

    if ativarEnvio:
        return requests.post(url, data=json.dumps(payload), headers=headers)
    else:
        return False


def sendMessageLog(message, number):
    if ativarLog:
        sendMessage(message, number)