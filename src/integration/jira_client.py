from jira import JIRA
import yaml
import os
import glob


from utils import log

logger = log.logger()
with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


class JiraClient:

    def __init__(self, token):
        '''
        :param token:
        Инициализируем jira, берем данные для подключения из config.yaml
        '''
        self.token = token
        separator = token.split(' ', 1)
        new_token = str(separator[1])
        self.jira = JIRA(config['links']['jira_link'], token_auth=new_token)

    def get_description(self, ticket: str) -> str:
        '''
        :param ticket:
        :return: issue_description
        Получаем название тикета по переданному идентификатору(ticket)
        '''
        issue = self.jira.issue(ticket)
        issue_description = issue.fields.description
        return issue_description

    def get_summary(self, ticket: str) -> str:
        '''
        :param ticket:
        :return: issue_summary
        Получаем содержимое описания тикета по переданному идентификатору(ticket)
        '''
        issue = self.jira.issue(ticket)
        issue_summary = issue.fields.summary
        return issue_summary

    def send_comment(self, jira_ticket: str, test_cases: str):
        '''
        :param jira_ticket:
        :param test_cases:
        Запись в комментарий переданных сгенерированных тестовых кейсов (test_cases)
        по переданному идентификатору тикета(jira_ticket)
        '''
        issue = self.jira.issue(jira_ticket)
        self.jira.add_comment(issue, test_cases)
        issue.update(fields={"labels": ["ctt_gpt"]}) #добавляем label в тикет для удобной фильтрации в Jira

    def create_ticket(self, bug_name: str, bug_steps: str, bug_or: str, bug_fr: str):
        '''
        :param bug_name:
        :param bug_steps:
        :param bug_or:
        :param bug_fr:
        Создание баг-репорта в Jira по переданному названию тикета (bug_name), шагам воспроизведения (bug_steps),
        ожидаемому результату (bug_or), фактическому результату (bug_fr).
        '''
        desc = "*Шаги воспроизведения:*\n" + str(bug_steps) + '\n*Ожидаемый результат:*\n' + str(
            bug_or) + '\n*Фактический результат:*\n' + str(bug_fr)
        new_issue = self.jira.create_issue(project='ERS', summary=str(bug_name),
                                           description=desc, issuetype={'name': 'Ошибка'}, components=[{'name': 'GPT'}])
        return new_issue

    def add_attachment(self, jira_id: str, name_photo_video):
        '''
        :param jira_id:
        :param name_photo_video:
        Добавление вложений с типом изображение/видеозапись по идентификатору тикета Jira (jira_id)
        и массиву вложений(name_photo_video)
        '''
        try:
            issue = self.jira.issue(jira_id)
            for x in name_photo_video:
                with open(x, 'rb') as f:
                    self.jira.add_attachment(issue=issue, attachment=f)
                files = glob.glob(x)
                for file in files:
                    os.remove(file)
        except Exception as e:
            logger.error(e)
            for x in name_photo_video:
                files = glob.glob(x)
            for file in files:
                os.remove(file)

    def send_jira_func(self, jira_ticket, test_cases):
        '''
        :param jira_ticket:
        :param test_cases:
        Функция отправки комментария в Jira по переданному идентификатору тикета (jira_ticket)
        и сгенерированным тестовым кейсам (test_cases)
        '''
        self.send_comment(self, jira_ticket, test_cases)
