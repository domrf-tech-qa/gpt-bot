from __future__ import annotations

import os
from datetime import datetime

import telebot
import re
from integration.jira_client import JiraClient
from utils import log
from integration.wiki import WikiClient
from utils import openapi
import schedule
import threading
import time
import yaml
from integration.testit import TestItClient
from utils.postgres import Postgres
import tg_buttons
from utils import regex
import generate_cases_functions
from utils import auth_token_functions
from utils import content_functions

logger = log.logger()
model = "yagpt"
token_jira = ''
token_wiki = ''
token_testit = ''
jiraTicket = ''
wiki_id = ''
testCases = ''
issueDescription = ''
api_doc = ''
api_method = ''
api_choice = ''
user_prompt = ''
testit_project = ''
bug_name = ''
bug_steps = ''
bug_or = ''
bug_fr = ''

with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
bot = telebot.TeleBot(config['bot_id'])

pg_queries = Postgres()


@bot.message_handler(commands=['start'])
def start_message(message):
    tg_buttons.help_button(message, bot)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id,
                     config['bot_messages']['help_message'])


@bot.message_handler(commands=['createBugReport'])
def bug_report(message):
    token_count = pg_queries.get_count_token_pg(message, 'jira_token')
    if token_count == 0:
        bot.send_message(message.from_user.id, config['bot_messages']['create_bug_unauthorized'])
    else:
        bot.send_message(message.from_user.id, config['bot_messages']['create_bug_authorized'])


@bot.message_handler(content_types=['photo'])
def photo(message):
   content_functions.photo_video_func(message, bot, "photo")


@bot.message_handler(content_types=['video'])
def video(message):
   content_functions.photo_video_func(message, bot, "video")


@bot.message_handler(commands=["clearAttachments"])
def clear_image(message):
    '''
    :param message:
    Функция очистки вложений для пользователя по команде /clearAttachments
    '''
    attach = pg_queries.get_attachments_by_user(message)
    for x in attach:
        os.remove(x[1])
        pg_queries.delete_attachments_by_id(x[0])

    bot.send_message(message.chat.id, config['bot_messages']['clear_attachments'])


@bot.message_handler(commands=['createPageObject'])
def create_pageobject(message):
    tg_buttons.gpt_buttons(message, bot)
    token_count = pg_queries.get_count_token_pg(message, 'wiki_token')
    if token_count == 0:
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_wiki_token'])
        bot.send_message(message.from_user.id, "3) " + config['bot_messages']['get_prompt_pageobject'])
        bot.send_message(message.from_user.id, "4) " + config['bot_messages']['get_wiki_pageid'])
    else:
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_prompt_pageobject'])
        bot.send_message(message.from_user.id, "3) " + config['bot_messages']['get_wiki_pageid'])


@bot.message_handler(commands=['clearSession'])
def clear_session(message):
    '''
    :param message:
    Функция очистки сессий в testit, jira, wiki для пользователя по команде /clearSession
    '''
    pg_queries.delete_session(message)
    bot.send_message(message.chat.id, "Сессия пользователя " + message.from_user.username + " очищена")


@bot.message_handler(commands=['sendToJira'])
def send_jira(message):
    global jiraTicket
    global testCases
    global token_jira
    try:
        if (jiraTicket != '') and (testCases != ''):
            try:
                token_jira = pg_queries.get_token_pg(message, 'jira_token')
                JiraClient(token_jira).send_jira_func(jiraTicket, testCases)
                bot.send_message(message.from_user.id,
                                 "В тикет " + config['links'][
                                     'jira_link'] + "browse/" + jiraTicket + " добавлен комментарий с разработанными тестовыми кейсами")
                jiraTicket = ''
                testCases = ''
            except Exception as e:
                logger.error(e)
                bot.send_message(message.from_user.id, config['bot_messages']['error_send_case_jira'])
        else:
            bot.send_message(message.from_user.id, config['bot_messages']['error_order_send_case_jira'])
    except Exception as e:
        logger.error(e)
        bot.send_message(message.from_user.id, config['bot_messages']['error_send_case_jira'])


@bot.message_handler(commands=['sendToWiki'])
def send_wiki(message):
    global wiki_id
    global testCases
    global token_wiki
    try:
        if (wiki_id != '') and (testCases != ''):
            try:

                wiki_token = pg_queries.get_token_pg(message, 'wiki_token')

                WikiClient(wiki_token).send_comment(wiki_id, testCases)

                bot.send_message(message.from_user.id,
                                 "В статью " + config['links'][
                                     'wiki_url'] + "/pages/viewpage.action?" + wiki_id + " добавлен комментарий с разработанными тестовыми кейсами")

                wiki_id = ''
                testCases = ''
            except Exception as e:
                logger.error(e)
                bot.send_message(message.from_user.id, config['bot_messages']['error_send_case_wiki'])
        else:
            bot.send_message(message.from_user.id, config['bot_messages']['error_order_send_case_jira'])
    except Exception as e:
        logger.error(e)
        bot.send_message(message.from_user.id, config['bot_messages']['error_send_case_wiki'])


@bot.message_handler(commands=['getjavatests'])
def java_tests(message):
    global testCases
    try:
        if testCases != '':
            try:
                testCases = generate_cases_functions.to_gpt(message, config['start_text']['api_java'], testCases,
                                                            api_choice,
                                                            model, bot)
                generate_cases_functions.send_result(message, testCases, bot)
                bot.send_message(message.from_user.id, config['bot_messages']['bug_report'])
                testCases = ''
            except Exception as e:
                logger.error(e)
                bot.send_message(message.from_user.id, config['bot_messages']['error_get_java_tests'])
        else:
            bot.send_message(message.from_user.id, config['bot_messages']['error_order_get_java_tests'])
    except Exception as e:
        logger.error(e)
        bot.send_message(message.from_user.id, config['bot_messages']['error_get_java_tests'])


@bot.message_handler(commands=['getpythontests'])
def python_tests(message):
    global testCases
    try:
        if testCases != '':
            try:
                testCases = generate_cases_functions.to_gpt(message, config['start_text']['api_python'], testCases,
                                                            api_choice, model, bot)
                generate_cases_functions.send_result(message, testCases, bot)
                bot.send_message(message.from_user.id, config['bot_messages']['bug_report'])
                testCases = ''
            except Exception as e:
                logger.error(e)
                bot.send_message(message.from_user.id, config['bot_messages']['error_get_python_tests'])

        else:
            bot.send_message(message.from_user.id, config['bot_messages']['error_order_get_python_tests'])
    except Exception as e:
        logger.error(e)
        bot.send_message(message.from_user.id, config['bot_messages']['error_get_python_tests'])


@bot.message_handler(commands=['getcasejira'])
def get_case_jira(message):
    tg_buttons.gpt_buttons(message, bot)
    token_count = pg_queries.get_count_token_pg(message, 'jira_token')
    if token_count == 0:
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_jira_token'])
        bot.send_message(message.from_user.id, "3) " + config['bot_messages']['get_ticket_jira'])
    else:
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_ticket_jira'])
    bot.register_next_step_handler(message, get_text_messages)


@bot.message_handler(commands=['sendToTestit'])
def send_testit(message):
    token_count_jira = pg_queries.get_count_token_pg(message, 'jira_token')
    if token_count_jira == 0:
        bot.send_message(message.from_user.id, "0) " + config['bot_messages']['get_jira_token'])
    token_count_testit = pg_queries.get_count_token_pg(message, 'testit_token')
    if token_count_testit == 0:
        bot.send_message(message.from_user.id, "1) " + config['bot_messages']['get_testit_token'])
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_testit_project'])
        bot.send_message(message.from_user.id, "3) " + config['bot_messages']['get_testit_section'])
    else:
        bot.send_message(message.from_user.id, "1) " + config['bot_messages']['get_testit_project'])
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_testit_section'])
    bot.register_next_step_handler(message, get_text_messages)


@bot.message_handler(commands=['getcasewiki'])
def get_case_wiki(message):
    tg_buttons.gpt_buttons(message, bot)
    token_count = pg_queries.get_count_token_pg(message, 'wiki_token')
    if token_count == 0:
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_wiki_token'])
        bot.send_message(message.from_user.id, "3) " + config['bot_messages']['get_wiki_pageid'])
    else:
        bot.send_message(message.from_user.id, "2) " + config['bot_messages']['get_wiki_pageid'])
    bot.register_next_step_handler(message, get_text_messages)


@bot.message_handler(commands=['getcaseapi'])
def get_case_api(message):
    tg_buttons.gpt_buttons(message, bot)
    bot.send_message(message.from_user.id, "2) " + config['bot_messages']['api_choice'])
    bot.send_message(message.from_user.id, "3) " + config['bot_messages']['get_apidoc'])
    bot.send_message(message.from_user.id, "4) " + config['bot_messages']['get_method'])
    bot.register_next_step_handler(message, get_text_messages)


@bot.message_handler(commands=['getMoreCases'])
def get_more_cases(message):
    global testCases
    global issueDescription
    if issueDescription != '' and testCases != '':
        test_cases_old = testCases
        testCases = generate_cases_functions.to_gpt_add(message, config['start_text']['cases'], issueDescription,
                                                        testCases, config['start_text']['more_cases'], model, bot)
        bot.send_message(message.from_user.id, "Кейсы готовы:")
        issueDescription = config['start_text']['more_cases']
        # Запись результатов в БД
        pg_queries.write_log(message, model, jiraTicket, issueDescription, testCases)
        # Записали результаты в БД
        generate_cases_functions.send_result(message, testCases, bot)
        testCases = test_cases_old + '\n\n*Дополнительные тестовые кейсы:*\n\n' + testCases
        bot.send_message(message.from_user.id, config['bot_messages']['get_more_cases_summary'])
        issueDescription = ''
    else:
        bot.send_message(message.from_user.id, config['bot_messages']['error_order_get_more_cases'])


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    '''
    :param message:
    Функция обработки текстовых сообщений ботом, логика построена на регулярных выражениях
    в случае, если сообщение, полученное от пользователя, совпадает с каким-либо регулярным выражением -
    запускается обработка, если нет - выдается сообщение, что пользователь ввел что-то необрабатываемое
    '''
    global model
    global jiraTicket
    global wiki_id
    global token_jira
    global token_wiki
    global testCases
    global issueDescription
    global api_doc
    global api_method
    global api_choice
    global user_prompt
    global token_testit
    global testit_project
    global bug_name
    global bug_steps
    global bug_or
    global bug_fr

    if message.text == "YaGPT":
        model = "yagpt"

    elif message.text == "YaGPT4":
        model = "yagpt4"

    elif re.match(regex.get_regex('tpl_bug_name'), message.text) is not None:
        bug_name = message.text.split(' ', 1)[1]

    elif re.match(regex.get_regex('tpl_bug_steps'), message.text) is not None:
        bug_steps = message.text.split(' ', 1)[1]

    elif re.match(regex.get_regex('tpl_bug_or'), message.text) is not None:
        bug_or = message.text.split(' ', 1)[1]

    elif re.match(regex.get_regex('tpl_bug_fr'), message.text) is not None:
        bug_fr = message.text.split(' ', 1)[1]
        token = pg_queries.get_token_pg(message, 'jira_token')
        jira_functions = JiraClient(token)
        ticket = jira_functions.create_ticket(bug_name, bug_steps, bug_or, bug_fr)
        name_photo_video = []
        all_files = os.listdir()
        for x in all_files:
            if re.match(message.from_user.username + '.*', x) is not None:
                name_photo_video.append(x)
        if len(name_photo_video) != 0:
            jira_functions.add_attachment(ticket, name_photo_video)
        name_photo_video.clear()
        bot.send_message(message.chat.id, "Bug report создан. Ссылка - " + config['links']['jira_link'] + "browse/" + str(ticket))

    elif re.match(regex.get_regex('tpl_prompt'), message.text) is not None:
        separator = message.text.split(' ', 1)
        user_prompt = str(separator[1])

    elif re.match(regex.get_regex('tpl_send_jira_ticket'), message.text) is not None:
        separator = message.text.split(' ', 1)
        jiraTicket = str(separator[1])
        bot.send_message(message.from_user.id, "Твой тикет для отправки кейсов " + jiraTicket)

    elif re.match(regex.get_regex('tpl_section_testit'), message.text) is not None:
        separator = message.text.split(' ', 1)
        testit_section = str(separator[1])
        bot.send_message(message.from_user.id, "Твоя секция в проекте TestIT " + testit_section)

        try:
            last_type = pg_queries.get_link(message)
            case_name = create_case_name(last_type, jiraTicket, wiki_id, api_method, api_doc, message)
            token_testit = pg_queries.get_token_pg(message, 'testit_token')

            testit_id, testit_global_id, new_section = TestItClient(token_testit).send_testit_func(testCases,
                                                                                                   testit_project,
                                                                                                   testit_section,
                                                                                                   case_name)

            if testit_id != '' and testit_section != '':
                bot.send_message(message.from_user.id,
                                 "Тестовые кейсы успешно созданы: " + config['links'][
                                     'testit_url'] + "/projects/" + str(
                                     testit_global_id) + "/tests?isolatedSection=" + new_section)

                wiki_id, jiraTicket, api_method, api_doc = '', '', '', ''
            else:
                bot.send_message(message.from_user.id, config['bot_messages']['error_parameter_testit'])
        except Exception as e:
            logger.error(e)
            bot.send_message(message.from_user.id, config['bot_messages']['error_testit'])

    elif re.match(regex.get_regex('tpl_jira_ticket'), message.text) is not None:
        jiraTicket = message.text
        bot.send_message(message.from_user.id, "Твой тикет " + jiraTicket)

        try:
            token_jira = pg_queries.get_token_pg(message, 'jira_token')
            issueDescription = JiraClient(token_jira).get_description(jiraTicket)

        except Exception as e:
            logger.error(e)
            bot.send_message(message.from_user.id,
                             "Что-то пошло не так, возможно " + jiraTicket + " не существует / Переданный токен не корректный")

        if issueDescription != '':
            testCases = generate_cases_functions.generate_case(message, issueDescription, model, jiraTicket,
                                                               api_choice,
                                                               'jira', bot)
    elif re.match(regex.get_regex('tpl_wiki_id'), message.text) is not None:
        wiki_id = message.text
        bot.send_message(message.from_user.id, "Твоя страница - " + wiki_id)

        try:
            token_wiki = pg_queries.get_token_pg(message, 'wiki_token')
            issueDescription = WikiClient(token_wiki).get_wiki_scenario(wiki_id)
        except Exception as e:
            logger.error(e)
            bot.send_message(message.from_user.id,
                             "Что-то пошло не так, возможно " + wiki_id + " не существует / Переданный токен не корректный")
        if issueDescription == '     ':
            bot.send_message(message.from_user.id,
                             "Что-то пошло не так, возможно структура " + wiki_id + " не подходит под требования для обработки ботом")
        if issueDescription != '' and not issueDescription.startswith('<'):
            testCases = generate_cases_functions.generate_case(message, issueDescription, model, wiki_id, api_choice,
                                                               'wiki', bot)
        elif issueDescription != '' and issueDescription.startswith('<'):
            testCases = generate_cases_functions.generate_case(message, issueDescription, model, wiki_id, api_choice,
                                                               'wiki', bot, user_prompt)
            issueDescription = ''

    elif re.match(regex.get_regex('tpl_project_testit'), message.text) is not None:
        testit_project = message.text
        bot.send_message(message.from_user.id, "Имя проекта в TestIT принято")
        separator = testit_project.split(' ', 1)
        testit_project = str(separator[1])

    elif re.match('/gettextcase', message.text) is not None:
        api_choice = 'textcase'
        bot.send_message(message.from_user.id, "Выбрана генерация тестовых кейсов для API")

    elif re.match('/getcurltests', message.text) is not None:
        api_choice = 'curltests'
        bot.send_message(message.from_user.id, "Выбрана генерация API тестов в формате CURL")

    elif re.match(regex.get_regex('tpl_apidoc'), message.text) is not None:
        api_doc = message.text
        bot.send_message(message.from_user.id, "Ссылка на api-doc принята")

    elif re.match(regex.get_regex('tpl_apimethod'), message.text) is not None:
        api_method = message.text
        bot.send_message(message.from_user.id, "Ссылка на Method принята")

        if api_choice != '' and api_doc != '' and api_method != '':
            try:
                issueDescription = openapi.get_json_api(api_method, api_doc)
            except Exception as e:
                logger.error(e)
                bot.send_message(message.from_user.id, config['bot_messages']['error_apidoc'])
        else:
            bot.send_message(message.from_user.id, config['bot_messages']['error_api_required_param'])

        testCases = generate_cases_functions.generate_case_api(message, issueDescription, model, api_choice, api_doc,
                                                               bot)
        api_choice = ''

    elif re.match(regex.get_regex('tpl_token_jira'), message.text) is not None:
        token_jira = message.text
        auth_token_functions.tokens(message, token_jira, 'jira_token', bot)

    elif re.match(regex.get_regex('tpl_token_testit'), message.text) is not None:
        token_testit = message.text
        auth_token_functions.tokens(message, token_testit, 'testit_token', bot)

    elif re.match(regex.get_regex('tpl_token_wiki'), message.text) is not None:
        token_wiki = message.text
        auth_token_functions.tokens(message, token_wiki, 'wiki_token', bot)

    else:
        bot.send_message(message.from_user.id, config['bot_messages']['error_text'])


def create_case_name(last_type, jira_ticket, wiki_id, api_method, api_doc, message) -> str:
    '''
    :param last_type:
    :param jira_ticket:
    :param wiki_id:
    :param api_method:
    :param api_doc:
    :param message:
    :return case_name:
    Функция создания имени секции в зависимости от того, из какого источника данных происходила генерация
    '''
    case_name = "Кейсы, сгенерированные ассистентом"
    if re.match(regex.get_regex('tpl_jira_ticket'), last_type):
        token_jira = pg_queries.get_token_pg(message, 'jira_token')
        summary = JiraClient(token_jira).get_summary(jira_ticket)
        case_name = jira_ticket + ": " + summary
    if re.match(regex.get_regex('tpl_wiki_id'), last_type):
        token_wiki = pg_queries.get_token_pg(message, 'wiki_token')
        wiki_title = WikiClient(token_wiki).get_title(wiki_id)
        case_name = "Проверка сценариев : " + wiki_title
    if re.match(regex.get_regex('tpl_apidoc'), last_type):
        case_name = "Тесты для метода: " + api_method + " по спецификации " + api_doc
    return case_name


def schedule_func():
    '''
    Функция запуска процессов по расписанию, очистка пользовательских данных раз в 12 часов
    Можно расширить необходимыми процессами
    '''
    try:
        schedule.every(12).hours.do(pg_queries.delete_session_job)
        schedule.every(12).hours.do(content_functions.delete_attach_job)
        while True:
            time.sleep(5)
            schedule.run_pending()
    except Exception as e:
        logger.error(e)


threading.Thread(target=schedule_func).start()
pg_queries.create_structure_pg()
bot.infinity_polling(timeout=10, long_polling_timeout=5)