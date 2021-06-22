import json
import requests
from src import acesso

ativarEnvio = False
ativarLog = True


def sendMessage(message, number):

    global ativarEnvio

    url = f'{acesso.getUrlApiWhats}'
    payload = {'message': f'{message}',
               'number': f'{number}'}
    headers = {'content-type': 'application/json',
               'accept': 'application/json',
               'Authorization': f'{acesso.getAuthorization}'}

    return requests.post(url, data=json.dumps(payload), headers=headers)


def sendMessageLog(message, number):

    global ativarLog

    if ativarLog:
        return sendMessage(message, number)
    else:
        return False


def sendMessageAlert(message, number):

    global ativarEnvio

    if ativarLog:
        return sendMessage(message, number)
    else:
        return False
