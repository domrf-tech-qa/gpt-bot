import psycopg2
from . import log
import yaml
from datetime import datetime
from . import scripts

logger = log.logger()


class Postgres:

    def __init__(self):
        self.__read_props()

    def __read_props(self):
        '''
        Инициализация подключения к БД, берем данные для подключения из config.yaml 
        '''
        with open("config.yaml", "r", encoding="utf8") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        self.user = config['database']['pg_user']
        self.password = config['database']['pg_password']
        self.host = config['database']['pg_host']
        self.port = config['database']['pg_port']
        self.database = config['database']['pg_database']

    def get_connection(self):
        '''
        Функция настройки коннекшена
        '''
        connection = psycopg2.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                                      database=self.database)
        connection.autocommit = True
        return connection

    def insert_pg(self, insert_query, record_to_insert):
        '''
        :param insert_query: 
        :param record_to_insert: 
        Функция выполнения insert запроса в БД по переданному sql (insert_query)
        и данных для записи (record_to_insert) 
        '''
        with self.get_connection() as connection, connection.cursor() as cursor:
            try:
                cursor.execute(insert_query, record_to_insert)
                logger.info('Record inserted successfully into table')
            except (Exception, psycopg2.Error) as error:
                logger.error('Failed to insert record into table', error)

    def select_pg(self, select_query):
        '''
        :param select_query: 
        :return: records (Возвращаем результирующую выборку по SQL запросу)
        Функция выполнения select запроса в БД по переданному sql (select_query)
        '''
        records = []
        with self.get_connection() as connection, connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
                records = cursor.fetchall()
                logger.info('Select from table successfully')
            except (Exception, psycopg2.Error) as error:
                logger.error('Failed to select records', error)
        return records

    def update_pg(self, update_query, record_to_update):
        '''
        :param update_query: 
        :param record_to_update: 
        Функция выполнения update запроса в БД по переданному sql (update_query)
        и данных для записи (record_to_update) 
        '''
        with self.get_connection() as connection, connection.cursor() as cursor:
            try:
                cursor.execute(update_query, record_to_update)
                logger.info('Records updated successfully')
            except (Exception, psycopg2.Error) as error:
                logger.error('Failed to insert record into table', error)

    def delete_pg(self, delete_query):
        '''
        :param delete_query: 
        Функция выполнения delete запроса в БД по переданному sql (delete_query)
        '''
        with self.get_connection() as connection, connection.cursor() as cursor:
            try:
                cursor.execute(delete_query)
                logger.info('Records deleted successfully')
            except (Exception, psycopg2.Error) as error:
                logger.error('Failed to delete record/s', error)

    def create_pg(self, create_query):
        '''
        :param delete_query: 
        Функция выполнения create запроса в БД по переданному sql (create_query)
        '''
        with self.get_connection() as connection, connection.cursor() as cursor:
            try:
                cursor.execute(create_query)
                logger.info('Table created successfully')
            except (Exception, psycopg2.Error) as error:
                logger.error('Failed to create table', error)

    def get_token_pg(self, message, system) -> str:
        token = self.select_pg(scripts.select_token_script.format(system, message.from_user.username))
        return token[0][0]

    def get_count_token_pg(self, message, system_token) -> str:
        token_count = self.select_pg(
            scripts.select_count_user_tokens_script.format(system_token, message.from_user.username))
        return token_count[0][0]

    def get_count_token_all_pg(self, message) -> str:
        token_count_all = self.select_pg(scripts.select_count_all_tokens_script.format(message.from_user.username))
        return token_count_all[0][0]

    def get_link(self, message) -> str:
        link = self.select_pg(scripts.select_link_script.format(message.from_user.username))
        return link[0][0]

    def delete_session(self, message):
        self.delete_pg(scripts.delete_session_script.format(message.from_user.username))

    def delete_session_job(self):
        current_date = datetime.today().strftime('%Y-%m-%d')
        self.delete_pg(scripts.delete_session_job_script.format(current_date))

    def write_log(self, message, model, link, issue_description, test_cases):
        now = datetime.now()
        record_to_insert = (
            message.from_user.username, message.from_user.first_name, message.from_user.last_name, model, link,
            issue_description, test_cases, now)
        self.insert_pg(scripts.insert_log_script, record_to_insert)

    def write_auth(self, message, token, field):
        now = datetime.now()
        record_to_insert = (message.from_user.username, token, now)
        self.insert_pg(scripts.insert_auth_script.format(field), record_to_insert)

    def update_auth(self, message, token, field):
        now = datetime.now()
        postgres_update_query = scripts.update_auth_script.format(field)
        record_to_update = (token, now, message.from_user.username)
        self.update_pg(postgres_update_query, record_to_update)

    def create_structure_pg(self):
        create_tables_scripts = scripts.create_tables_scripts
        for script in create_tables_scripts:
            self.create_pg(script)
