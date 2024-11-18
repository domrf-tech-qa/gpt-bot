select_token_script = 'Select {0} from public.gpt_auth where tg_username = \'{1}\''
select_count_user_tokens_script = 'Select count({0}) from public.gpt_auth where tg_username = \'{1}\''
select_count_all_tokens_script = 'Select count(*) from public.gpt_auth where tg_username = \'{0}\''
select_link_script ='Select link from public.gpt_log where tg_username = \'{0}\' and link != \'\' ORDER BY TIME desc limit 1;'
delete_session_script = 'delete from public.gpt_auth WHERE tg_username = \'{0}\''
delete_session_job_script = 'delete from public.gpt_auth WHERE TIME < \'{0}\''
insert_log_script = 'INSERT INTO public.gpt_log (tg_username, tg_firstname, tg_lastname, gpt_model,link,prom,response,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
insert_auth_script = 'INSERT INTO public.gpt_auth (tg_username, {0},  time) VALUES (%s,%s,%s)'
update_auth_script = 'Update public.gpt_auth SET {0} = %s, time = %s where tg_username = %s'
create_tables_scripts = ["CREATE TABLE IF NOT EXISTS \"gpt_auth\" ( \"tg_username\" VARCHAR(150) NULL DEFAULT NULL, \"wiki_token\" VARCHAR(150) NULL DEFAULT NULL, \"testit_token\" VARCHAR(150) NULL DEFAULT NULL, \"jira_token\" VARCHAR(150) NULL DEFAULT NULL, \"time\" TIMESTAMP NULL DEFAULT NULL);",
                       "CREATE TABLE IF NOT EXISTS \"gpt_log\" (\"tg_username\" VARCHAR(150) NULL DEFAULT NULL,\"tg_firstname\" VARCHAR(150) NULL DEFAULT NULL,\"tg_lastname\" VARCHAR(150) NULL DEFAULT NULL,\"gpt_model\" VARCHAR NULL DEFAULT NULL,\"link\" VARCHAR NULL DEFAULT \'NULL\',\"prom\" VARCHAR NULL DEFAULT NULL,\"response\" VARCHAR NULL DEFAULT NULL,\"time\" TIMESTAMP NULL DEFAULT NULL);",
                       "CREATE TABLE IF NOT EXISTS \"message\" (\"username\" VARCHAR NULL DEFAULT NULL,\"chatid\" VARCHAR NULL DEFAULT NULL,\"title\" VARCHAR NULL DEFAULT NULL,\"text\" VARCHAR NULL DEFAULT NULL,\"result\" VARCHAR NULL DEFAULT NULL,\"date\" BIGINT NULL DEFAULT NULL);"
    ]