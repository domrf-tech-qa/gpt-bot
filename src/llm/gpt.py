from __future__ import annotations
from g4f.client import Client
import os
from ..utils import log

logger = log.logger()


def ask_gpt(prom: str) -> str:
    '''
    :param prom:
    :return: response.choices[0].message.content (возвращаем сгенерированные данные)
    Функция генерации кейсов через g4f (https://github.com/xtekky/gpt4free) по переданному prompt запросу (prom)
    '''
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prom}],
        )
    except Exception as e:
        logger.error(e)
        response.choices[0].message.content = 'К сожалению у gpt возникли проблемы, попробуй позже'
    return response.choices[0].message.content
