def get_regex(key:str)->str():
    '''
    :param key: 
    :return: regex_dict.get(key) (возвращаем value)
    Функция - словарь для получения значения regex по переданному key
    '''
    regex_dict = {}
    regex_dict['tpl_jira_ticket'] = '\w*-\d*'
    regex_dict['tpl_send_jira_ticket'] = 'send \w*-\d*'
    regex_dict['tpl_token_jira'] = 'JiraToken .*'
    regex_dict['tpl_project_testit'] = 'TestitProject .*'
    regex_dict['tpl_wiki_id'] = '\w*=\d*'
    regex_dict['tpl_token_wiki'] = 'WikiToken .*'
    regex_dict['tpl_token_testit'] = 'TestitToken .*'
    regex_dict['tpl_section_testit'] = 'TestitSection .*'
    regex_dict['tpl_apidoc'] = 'Apidoc .*'
    regex_dict['tpl_apimethod'] = 'Method .*'
    regex_dict['tpl_prompt'] = 'Prompt .*'
    regex_dict['tpl_bug_name'] = 'Название .*'
    regex_dict['tpl_bug_steps'] = 'Шаги .*'
    regex_dict['tpl_bug_or'] = 'ОР .*'
    regex_dict['tpl_bug_fr'] = 'ФР .*'
    return regex_dict.get(key)
