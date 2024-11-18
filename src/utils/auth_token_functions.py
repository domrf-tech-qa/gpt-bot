from .postgres import Postgres

pg_queries = Postgres()


def tokens(message, token, system, bot):
    '''
    :param message: 
    :param token: 
    :param system: 
    :param bot: 
    Функция работы с токенами для jira, wiki, testIT по переданным параметрам - message, token, system, bot
    '''
    token_count = pg_queries.get_count_token_pg(message, system)
    token_count_all = pg_queries.get_count_token_all_pg(message)
    if token_count == 0:
        if token_count_all == 0:
            pg_queries.write_auth(message, token, system)
        else:
            pg_queries.update_auth(message, token, system)
        if system == 'jira_token':
            bot.send_message(message.from_user.id, "Токен Jira принят ")
        if system == 'testit_token':
            bot.send_message(message.from_user.id, "Токен Testit принят ")
        if system == 'wiki_token':
            bot.send_message(message.from_user.id, "Токен Wiki принят ")
