import yaml
from utils.postgres import Postgres
from utils import log
from llm import yagpt

logger = log.logger()
with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

pg_queries = Postgres()


def generate_case(message, issue_description, model, link, api_choice, type, bot, user_prompt=''):
    '''
    :param message:
    :param issue_description:
    :param model:
    :param link:
    :param api_choice:
    :param type:
    :param bot:
    :param user_prompt:
    :return test_cases (возвращаем сгенерированные тестовые кейсы)
    Функция подготовки к отправке промпта в GPT для генерации тестовых кейсов по wiki/jira c передачей всех необходимых
    параметров для генерации.
    Необязательный параметр user_prompt используется только для генерации PageObject
    '''
    if user_prompt == '':
        test_cases = to_gpt(message, config['start_text']['cases'], issue_description, api_choice, model, bot)
    else:
        test_cases = to_gpt(message, user_prompt, issue_description, api_choice, model, bot)
    bot.send_message(message.from_user.id, "Кейсы готовы:")
    # Запись результатов в БД
    pg_queries.write_log(message, model, link, issue_description, test_cases)
    # Записали результаты в БД
    send_result(message, test_cases, bot)
    if type == 'jira':
        bot.send_message(message.from_user.id, config['bot_messages']['cases_jira_result'])
    if type == 'wiki' and user_prompt == '':
        bot.send_message(message.from_user.id, config['bot_messages']['cases_wiki_result'])
    if type == 'wiki' and user_prompt != '':
        bot.send_message(message.from_user.id,
                         "Если хочешь опубликовать кейсы комментарием в статью на Wiki выполни /sendToWiki ")
    return test_cases


def generate_case_api(message, issue_description, model, api_choice, api_doc, bot):
    '''
    :param message:
    :param issue_description:
    :param model:
    :param api_choice:
    :param api_doc:
    :param bot:
    :return test_cases (возвращаем сгенерированные тестовые кейсы):
    Функция подготовки к отправке промпта в GPT для генерации тестовых кейсов для API c передачей всех необходимых
    параметров для генерации.
    Необязательный параметр user_prompt используется только для генерации PageObject
    '''
    test_cases = ''
    if issue_description != '':
        if api_choice == 'textcase':
            if "swagger" not in api_doc:
                test_cases = to_gpt(message, config['start_text']['api'], issue_description, api_choice, model, bot)
            else:
                test_cases = to_gpt(message, config['start_text']['api_swagger'], issue_description, api_choice, model,
                                    bot)
        if api_choice == 'curltests':
            if "swagger" not in api_doc:
                test_cases = to_gpt(message, config['start_text']['api_curl'], issue_description, api_choice, model, bot)
            else:
                test_cases = to_gpt(message, config['start_text']['api_curl_swagger'], issue_description, api_choice,
                                    model, bot)
        bot.send_message(message.from_user.id, "Кейсы готовы:")
        # Запись результатов в БД
        pg_queries.write_log(message, model, api_doc, issue_description, test_cases)
        # Записали результаты в БД
        send_result(message, test_cases, bot)
        bot.send_message(message.from_user.id, config['bot_messages']['cases_api_result'])
        if api_choice == 'curltests':
            bot.send_message(message.from_user.id, config['bot_messages']['curl_to_code'])
    return test_cases


def to_gpt(message: str, start_text: str, issue_description: str, api_choice: str, model: str, bot) -> str:
    '''
    :param message:
    :param start_text:
    :param issue_description:
    :param api_choice:
    :param model:
    :param bot:
    :return: test_cases (возвращаем сгенерированные тестовые кейсы):
    Функция отправки промта в gpt в зависимости от выбранной модели (model)
    '''
    test_cases = ''
    if model == 'yagpt' and issue_description != '' and issue_description is not None:
        bot.send_message(message.from_user.id, "Выбран инструмент - YaGPT")
        if api_choice == 'curltests':
            test_cases = yagpt.yandex_gpt(start_text + issue_description, "3")
        else:
            test_cases = yagpt.yandex_gpt(start_text + issue_description + config['start_text']['formater'], "3")
    elif model == 'yagpt4' and issue_description != '' and issue_description is not None:
        bot.send_message(message.from_user.id, "Выбран инструмент - YaGPT4")
        if api_choice == 'curltests':
            test_cases = yagpt.yandex_gpt(start_text + issue_description, "4")
        else:
            test_cases = yagpt.yandex_gpt(start_text + issue_description + config['start_text']['formater'], "4")
    else:
        bot.send_message(message.from_user.id, "В источнике нет данных для генерации")
    return test_cases


def to_gpt_add(message: str, start_text: str, issue_description: str, response: str, new_prompt: str, model: str,
               bot) -> str:
    '''
    :param message:
    :param start_text:
    :param issue_description:
    :param response:
    :param new_prompt:
    :param model:
    :param bot:
    :return: test_cases (возвращаем сгенерированные тестовые кейсы):
    Функция отправки в gpt запроса на генерацию дополнительных тестовых кейсов
    '''
    bot.send_message(message.from_user.id, "Дополнительная генерация кейсов")
    if model == 'yagpt':
        test_cases = yagpt.yandex_gpt(new_prompt, "3", start_text + issue_description, response)
    if model == 'yagpt4':
        test_cases = yagpt.yandex_gpt(new_prompt, "4", start_text + issue_description, response)
    return test_cases


def send_result(message, testCases: str, bot):
    '''
    :param message:
    :param testCases:
    :param bot:
    Функция отправки результатов генерации обратно в telegram
    '''
    try:
        bot.send_message(message.from_user.id, testCases)
    except Exception as e:
        logger.error(e)
        bot.send_message(message.from_user.id, 'Пришел большой объем данных, придется разбить на несколько сообщений')
        big_response = testCases
        mean_index = len(big_response) // 2
        part_1 = big_response[:mean_index]
        part_2 = big_response[mean_index:]
        try:
            bot.send_message(message.from_user.id, part_1)
            bot.send_message(message.from_user.id, part_2)
        except Exception as e:
            logger.error(e)
            mean_index = len(part_1) // 2
            part_1_1 = part_1[:mean_index]
            part_1_2 = part_1[mean_index:]
            part_2_1 = part_2[:mean_index]
            part_2_2 = part_2[mean_index:]
            bot.send_message(message.from_user.id, part_1_1)
            bot.send_message(message.from_user.id, part_1_2)
            bot.send_message(message.from_user.id, part_2_1)
            bot.send_message(message.from_user.id, part_2_2)
