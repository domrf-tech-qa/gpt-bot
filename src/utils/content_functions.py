import os
import time
import re
import yaml


with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def photo_video_func(message, bot, type: str):
    '''
    :param message: 
    :param bot: 
    :param type: 
    Функция обработки контента видео и фото, сохранения контента на фх внутри контейнера
    передаваемые параметры - message, bot, type (photo/video)
    '''
    all_files = get_files()
    counter = get_count_files(all_files, message, type)
    if type == "photo":
        if counter > 4:
            bot.send_message(message.chat.id,
                                   config['bot_messages']['limit_photo'])
        else:
            result_message = bot.send_message(message.chat.id, config['bot_messages']['load_photo'],
                                                    parse_mode='HTML', disable_web_page_preview=True)
        file_id = message.photo[-1].file_id
    if type == "video":
        if counter > 1:
           bot.send_message(message.chat.id,
                                   config['bot_messages']['limit_video'])
        else:
            result_message = bot.send_message(message.chat.id, config['bot_messages']['load_video'],
                                                    parse_mode='HTML', disable_web_page_preview=True)
        file_id = message.video.file_id
    path = bot.get_file(file_id)
    downloaded_file = bot.download_file(path.file_path)
    extn = '.' + str(path.file_path).split('.')[-1]
    name = message.from_user.username + type + str(time.time()) + extn
    with open(name, 'wb') as new_file:
        new_file.write(downloaded_file)
    if type == 'photo':
         bot.edit_message_text(chat_id=message.chat.id, message_id=result_message.id,
                                    text=config['bot_messages']['load_image_p1'] + str(counter + 1)
                                         + config['bot_messages']['load_image_p2'], parse_mode='HTML')
    if type == 'video':
         bot.edit_message_text(chat_id=message.chat.id, message_id=result_message.id,
                                    text=config['bot_messages']['load_video_p1'] + str(counter + 1)
                                         + config['bot_messages']['load_video_p2'], parse_mode='HTML')



def get_count_files(all_files, message, type):
    counter = 0
    for x in all_files:
        if re.match(message.from_user.username + type + '.*', x) is not None:
            counter = counter + 1
    return counter


def get_files():
    all_files = os.listdir()
    return all_files
