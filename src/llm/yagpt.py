from __future__ import annotations
import requests
import json
import yaml


with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def getToken() -> str:
    '''
    :return: data['iamToken'] (Возвращаем токен для взаимодействия с yagpt)
    Функция получения токена в yagpt
    '''
    url = config['links']['yandex_gpt_token_url']
    myobj = {'yandexPassportOauthToken': config['auth']['yandexPassportOauthToken']}
    x = requests.post(url, json=myobj)
    data = json.loads(x.text)
    return data['iamToken']


def yandex_gpt(prom: str, model: str, old_prompt='', old_response=''):
    '''
    :param prom: 
    :param model: 
    :param old_prompt: 
    :param old_response: 
    :return: data['result']['alternatives'][0]['message']['text'] (возвращаем сгенерированные данные)
    Функция генерации кейсов через yagpt по переданному prompt - запросу (prom), параметру model, который отвечает
    за используемую версию yagpt
    параметры old_prompt и old_response используются для генерации дополнительных кейсов через функцию /getMoreCases 
    '''
    model_uri = ""
    if model == "3":
        model_uri = "gpt://" + config['auth']['folder_id'] + "/yandexgpt/latest"
    if model == "4":
        model_uri = "gpt://" + config['auth']['folder_id'] + "/yandexgpt-32k/rc"
    if old_prompt == '' and old_response == '':
        messages = [
            {
                "role": "user",
                "text": prom
            }
        ]
    else:
        messages = [
            {
                "role": "user",
                "text": old_prompt
            },
            {
                "role": "assistant",
                "text": old_response
            },
            {
                "role": "user",
                "text": prom
            }
        ]
    response = requests.post(
        config['links']['yandex_gpt_api_url'],
        headers={
            "Authorization": f"Api-Key {config['auth']['yandexgpt_key']}",
            "x-folder-id": config['auth']['folder_id']
        },
        json={
            "modelUri": model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.6
            },
            "messages": messages
        },
    )
    data = response.json()
    return data['result']['alternatives'][0]['message']['text']
