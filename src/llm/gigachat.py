from __future__ import annotations
import requests
import json
import uuid
import yaml

with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def get_token() -> str:
    '''
    Функция получения токена для GigaChat, возвращает access_token
    '''
    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': config['auth']['gigachat_auth']
    }
    response = requests.request("POST", config['links']['gigachat_auth_link'], headers=headers, data=payload,
                                verify=False)
    data = json.loads(response.text)
    return data['access_token']


def gigachat_gpt(prom: str):
    '''
    :param prom:
    :return: data['choices'][0]['message']['content'] (возвращаем сгенерированные данные)
    Функция генерации кейсов через GigaChat по переданному prompt запросу (prom)
    '''
    payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": prom
            }
        ],
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 10000,
        "repetition_penalty": 1
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + get_token()
    }
    response = requests.request("POST", config['links']['gigachat_gpt_link'], headers=headers, data=payload,
                                verify=False)
    data = response.json()
    return data['choices'][0]['message']['content']
