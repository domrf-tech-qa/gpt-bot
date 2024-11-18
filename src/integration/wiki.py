from atlassian import Confluence
from lxml import html

import yaml

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class WikiClient:

    def __init__(self, token):
        '''
        :param token:
        Инициализируем Wiki, берем данные для подключения из config.yaml
        '''
        self.token = token
        separator = token.split(' ', 1)
        new_token = str(separator[1])
        self.confluence = Confluence(url=config['links']['wiki_url'], token=new_token)

    def get_wiki_scenario(self, page_id: str) -> str:
        '''
        :param page_id:
        :return: test_str (возвращаем собранную информацию в формате строки)
        Функция сбора данных с wiki для генерации кейсов по ним
        условия парсинга реализованы под нашу специфику работы
        необходимо кастомизировать под свои требования
        '''
        separator = page_id.split('=', 1)
        page_id = str(separator[1])
        pg_title = self.confluence.get_page_by_id(page_id, expand='title')
        pg_body = self.confluence.get_page_by_id(page_id, expand='body.storage')
        pg_content = pg_body['body']['storage']['value']
        parsed_html = BeautifulSoup(pg_content, 'html.parser')
        table = str(parsed_html.find_all('table'))
        test_str = create_string('//th/*[contains(text(),\'Предусловия\')]/../../td//text()',
                                 '//th/*[contains(text(),\'Предусловия\')]/text()', table) + ' '
        test_str = test_str + create_string('//th/*[contains(text(),\'Основной сценарий\')]/../../td//text()',
                                            '//th/*[contains(text(),\'Основной сценарий\')]/text()', table) + ' '
        test_str = test_str + create_string('//th/*[contains(text(),\'Альтернативный сценарий\')]/../../td//text()',
                                            '//th/*[contains(text(),\'Альтернативный сценарий\')]/text()', table) + ' '
        test_str = test_str + create_string('//th/*[contains(text(),\'Сценарий\')]/../../td//text()',
                                            '//th/*[contains(text(),\'Сценарий\')]/text()', table) + ' '
        test_str = test_str + create_string('//th/*[contains(text(),\'Постусловия\')]/../../td//text()',
                                            '//th/*[contains(text(),\'Постусловия\')]/text()', table) + ' '
        if (("ТИМ" in pg_title['title'] and test_str == '     ') or (
                "US" in pg_title['title'] and test_str == '     ') or (
                "Generate" in pg_title['title'] and test_str == '     ')):
            ph = str(parsed_html.text)
            test_str = prepare_string(ph)
        return test_str

    def send_comment(self, wiki_id: str, test_cases: str):
        '''
        :param wiki_id:
        :param test_cases:
        Функция отправки комментария со сгенерированными тестовыми кейсами по переданному идентификатору статьи (wiki_id)
        и сгенерированным тестовым кейсам (testCases)
        '''
        separator = wiki_id.split('=', 1)
        wiki_id = str(separator[1])
        self.confluence.add_comment(wiki_id, test_cases)
        self.confluence.set_page_label(wiki_id, 'ctt_gpt')

    def get_title(self, page_id: str):
        '''
        :param page_id:
        :return: pg_title['title'] (возвращается заголовок статьи)
        Функция получения заголовка статьи по переданному идентификатору (page_id)
        '''
        separator = page_id.split('=', 1)
        page_id = str(separator[1])
        pg_title = self.confluence.get_page_by_id(page_id, expand='title')
        return pg_title['title']


def parse_by_xpath(xpath: str, table: str) -> str:
    '''
    :param xpath:
    :param table:
    :return: parsed (возвращаем распаршенное значение)
    Функция парсинга данных по переданнму xpath (xpath) и html элементу, из которого парсим
    '''
    tree = html.fromstring(table)
    parsed = tree.xpath(xpath)
    return parsed


def create_string(xpath: str, xpath_text: str, table: str) -> str:
    '''
    :param xpath: 
    :param xpath_text: 
    :param table: 
    :return: res_string (возвращаем сформированную строку)
    Функция сбора строки
    '''
    try:
        preconditions = parse_by_xpath(xpath, table)
        res_arr = parse_by_xpath(xpath_text, table)
        if len(res_arr) == 1:
            res_string = res_arr[0] + ' '
            for i in preconditions:
                res_string = res_string + i + ' '
        else:
            res_string = 'Сценарий: '
            for i in preconditions:
                res_string = res_string + i + ' '
            if res_string == 'Сценарий: ':
                res_string = ''
    except Exception as e:
        res_string = ''
    return res_string


def prepare_string(ph: str) -> str:
    '''
    :param ph: 
    :return: result (возвращаем строку после трансформаций)
    Функция трансформации строки 
    '''
    ph = ph.replace('small', '')
    ph = ph.replace('.', '. ')
    ph = ph.replace('  ', ' ')
    ph = ph.replace(',', ', ')
    ph = ph.replace('  ', ' ')
    ph = ph.replace(':', ': ')
    ph = ph.replace('  ', ' ')
    ph = ph.replace(';', '; ')
    ph = ph.replace('  ', ' ')
    result = ph[0]
    for letter in ph[1:]:
        if letter.isupper():
            result += f' {letter}'
        else:
            result += letter
    result = result.replace('  ', ' ')
    return result
