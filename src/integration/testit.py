import requests
import testit_api_client
from testit_api_client import ApiClient, ApiException
import re
import yaml
from testit_api_client.api import work_items_api
from testit_api_client.model.work_item_entity_types import WorkItemEntityTypes
from testit_api_client.model.work_item_states import WorkItemStates
from testit_api_client.model.work_item_priority_model import WorkItemPriorityModel
from testit_api_client.model.create_work_item_request import CreateWorkItemRequest
from testit_api_client.api import sections_api
from testit_api_client.model.create_section_request import CreateSectionRequest

with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class TestItClient:

    def __init__(self, token):
        '''
        :param token:
        Инициализируем TestIt, берем данные для подключения из config.yaml
        '''
        self.token = token
        separator = token.split(' ', 1)
        self.new_token = str(separator[1])
        self.configuration = testit_api_client.Configuration(
            host=config['links']['testit_url'])

    def create_testcase(self, project_id, section_id, case_name, cases):
        '''
        :param project_id:
        :param section_id:
        :param case_name:
        :param cases:
        :return: f (возвращается global_id созданной сущности)
        Функция создание тестового кейса в TestIT с использованием "testit_api_client"
        по переданному идентификатору проекта (project_id),
        переданному идентификатору секции (section_id), переданному названию тестового кейса (case_name),
        переданным шагам тестового кейса (cases)
        '''
        with ApiClient(self.configuration,
                       header_name='Authorization',
                       header_value='PrivateToken ' + self.new_token) as api_client:
            api_instance = work_items_api.WorkItemsApi(api_client)
            testcase_model = {
                "entity_type_name": WorkItemEntityTypes("TestCases"),
                "project_id": project_id,
                "priority": WorkItemPriorityModel("Medium"),
                "section_id": section_id,
                "name": case_name,
                "state": WorkItemStates("NeedsWork"), #статус "Требуется доработки", чтобы тестировщики проверили сгенерированные кейсы
                "steps": cases,
                "precondition_steps": [],
                "postcondition_steps": [],
                "tags": [],
                "links": [],
                "attributes": {},
                "duration": 60,
            }
            create_work_item_request = CreateWorkItemRequest(testcase_model)
            api_response = api_instance.create_work_item(create_work_item_request=create_work_item_request)
            m = re.findall(",\W\W'global_id'[^:]*:.*", str(api_response)) #забираем параметр global_id
            separator = str(m).split(': ', 1)
            f = str(separator[1])
            separator = f.split(',\"]')
            f = str(separator[0])
            return f

    def create_section(self, project_id, section_id, case_name):
        '''
        :param project_id:
        :param section_id:
        :param case_name:
        :return: f (возвращаем id созданной сущности)
        Функция создания секции в TestIT по переданному идентификатору проекта (project_id),
        идентификатор корневой секции, в которой создается подсекция (section_id),
        название создаваемой секции (case_name)
        '''
        with ApiClient(self.configuration,
                       header_name='Authorization',
                       header_value='PrivateToken ' + self.new_token) as api_client:
            api_instance = sections_api.SectionsApi(api_client)
            section_model = {
                "project_id": project_id,
                "parent_id": section_id,
                "name": case_name,
                "attachments": []
            }
            create_section_request = CreateSectionRequest(section_model)
            api_response = api_instance.create_section(create_section_request=create_section_request)
            m = re.findall(",\W\W'id'[^:]*:.*", str(api_response)) #забираем параметр id
            separator = str(m).split(': ', 1)
            f = str(separator[1])
            separator = f.split(',\"]')
            f = str(separator[0])
            f = f.replace('\'', '')
            return f

    def parse_case(self, tc, project_id, section_id):
        '''
        :param tc:
        :param project_id:
        :param section_id:
        Функция парсинга тестовых кейсов, сгенерированных gpt, по переданным исходным кейсам от gpt (tc),
        переданному идентификатору проекта (project_id),
        переданному идентификатору секции, где будет создан тестовый кейс (section_id)
        '''
        cases = []
        tokens = re.split('Тестовый кейс', tc)
        del tokens[0]
        for x in range(len(tokens)):
            separator_new = []
            '''
            Блок вариаций, которые могут придти от gpt
            '''
            if "**Ожидаемый результат**" in tokens[x]:
                separator_new = tokens[x].split('**Ожидаемый результат**', 1)
            elif "*Ожидаемый результат*" in tokens[x]:
                separator_new = tokens[x].split('*Ожидаемый результат*', 1)
            elif "Ожидаемый результат" in tokens[x]:
                separator_new = tokens[x].split('Ожидаемый результат', 1)
            elif "**Ожидаемые результаты**" in tokens[x]:
                separator_new = tokens[x].split('**Ожидаемые результаты**', 1)
            '''
            Очистка данных от лишних символов
            '''
            step = str(separator_new[0])
            expected = str(separator_new[1])
            expected = expected.replace(": ", "")
            expected = expected.replace("**", "")
            expected = expected.replace("**", "")
            expected = expected.upper()
            sep = step.split('**', 1)
            case_name = str(sep[0])
            step = str(sep[1])
            cases.append({"action": step, "expected": expected})
            self.create_testcase(project_id, section_id, case_name, cases)
            cases = []

    def send_testit_func(self, testCases, testit_project, testit_section, case_name):
        '''
        :param testCases:
        :param testit_project:
        :param testit_section:
        :param case_name:
        :return: testit_id, testit_global_id, new_section
        Агрегирующая функция создания тестовых кейсов
        '''
        testit_id = get_projectid(testit_project, self.new_token)
        testit_global_id = get_global_projectid(testit_project, self.new_token)
        if testit_id != '' and testit_section != '':
            new_section = self.create_section(testit_id, testit_section, case_name)
            self.parse_case(testCases, testit_id, new_section)
        else:
            return '', '', ''
        return testit_id, testit_global_id, new_section


def get_projectid(search_value, new_token):
    '''
    :param search_value:
    :param new_token:
    :return: project_id
    Функция для получения идентификатора проекта по переданному названию проекта (search_value), и токену (new_token)
    реализуется через прямое обращение к API TestIT,
    так как из-за несовместимости версий "testit_api_client" и версии продукта, установленной в нашем контуре,
    '''
    url = config['links']['testit_url'] + '/api/v2/projects/search'
    myobj = {'name': search_value}
    try:
        api_response = requests.post(url, headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "PrivateToken " + new_token
        }, json=myobj, verify=False)
        data = api_response.json()
        project_id = data[0]['id']
    except ApiException as e:
        print("Exception when calling ProjectsApi->api_v2_projects_search_post: %s\n" % e)
    return project_id


def get_global_projectid(search_value, new_token):
    '''
    :param search_value:
    :param new_token:
    :return: global_project_id
    Функция для получения глобального идентификатора проекта по переданному названию проекта (search_value),
    и токену (new_token) реализуется через прямое обращение к API TestIT,
    так как из-за несовместимости версий "testit_api_client" и версии продукта, установленной в нашем контуре,
    '''
    url = config['links']['testit_url'] + '/api/v2/projects/search'
    myobj = {'name': search_value}
    try:
        api_response = requests.post(url, headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "PrivateToken " + new_token
        }, json=myobj, verify=False)
        data = api_response.json()
        global_project_id = data[0]['globalId']
    except testit_api_client.ApiException as e:
        print("Exception when calling ProjectsApi->api_v2_projects_search_post: %s\n" % e)
    return global_project_id