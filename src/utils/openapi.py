from . import log
import requests

logger = log.logger()


def get_json_api(api_path: str, api_docs_url: str) -> str:
    '''
    :param api_path:
    :param api_docs_url:
    :return: prepared_string (отдаем подготовленные данные для генерации кейсов по ним)
    Функция парсинга openapi спецификации по переданному контексту метода (api_path)
    и ссылке на спецификацию (api_docs_url)
    '''
    try:
        separator = api_path.split(' ', 1)
        api_path = str(separator[1])
        separator = api_docs_url.split(' ', 1)
        api_docs_url = str(separator[1])
        response = requests.get(api_docs_url)
        data = response.json()
        separator = str(data).split("\'paths\'", 1)
        first_data = str(separator[0])
        current_api = str(data['paths'][api_path])
        if "swagger" not in api_docs_url:
            schemas_arr = []
            for key in data['components']['schemas']:
                if key in current_api:
                    schemas_arr.append(key)
            for i in range(len(schemas_arr)):
                schemas_str = str(data['components']['schemas'][schemas_arr[i]])
                current_api = current_api.replace(str(schemas_arr[i]), schemas_str)
                current_api = current_api.replace('#/components/schemas/', '')
        prepared_string = first_data + '\'paths\':{' + api_path + ':' + current_api
        print(prepared_string)
    except Exception as e:
        logger.error(e)
    return prepared_string
