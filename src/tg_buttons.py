from telebot import types
import yaml

with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def gpt_buttons(message, bot):
    '''
    :param message: 
    :param bot: 
    Функция для кнопок выбора модели, можно кастомизировать, поменять стили итд.
    '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("YaGPT")
    btn2 = types.KeyboardButton("YaGPT4")
    btn3 = types.KeyboardButton("/help")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     text="1) " + config['bot_messages']['llm_choise'].format(
                         message.from_user), reply_markup=markup)


def help_button(message, bot):
    '''
    :param message: 
    :param bot: 
    Функция для кнопки /help, можно кастомизировать, поменять стили итд.
    '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/help")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text=config['bot_messages']['welcome_message'].format(
                         message.from_user), reply_markup=markup)
