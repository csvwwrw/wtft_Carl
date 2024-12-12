import telebot
import logging
import time
from mountables import logger_setup
from mountables.config_lib import config

###   НАСТРОЙКА ЛОГГЕРА   ###
logger = logging.getLogger('')
    
logger_setup.double_logger_setup('carl_chatbot.log', 'carl_chatbot_error.log', logger = logger)

###   РЕГИСТРАЦИЯ БОТА   ###

bot = telebot.TeleBot(config.TG_TOKEN)   

messages_folder = 'mountables/messages'
backend_tg = config.backend_tg

###   приветствие в личных сообщениях   ###
@bot.message_handler(chat_types = ['private'], commands=['start', 'help'])
def start_message(message):
    bot.send_message(message.from_user.id,
                     text = open(f'{messages_folder}/welcome.txt', 'r', encoding="utf-8").read(),
                     parse_mode = 'HTML')
    logger.info(f'Карл рассказал о себе {message.from_user.username}')

###   инфа о рекламе   ###
@bot.message_handler(chat_types = ['private'], commands=['ads'])
def ads_message(message):
    bot.send_message(backend_tg,
                     text = f"Юзер @{message.from_user.username} запросил информацию о рекламе.")
    bot.send_message(message.from_user.id, 
                     text = open(f'{messages_folder}/rules.txt', 'r', encoding="utf-8").read(), 
                     parse_mode = 'HTML')
    time.sleep(.5)
    bot.send_photo(message.from_user.id,
                   open(f'{messages_folder}/price.png', 'rb'),
                   caption = open(f'{messages_folder}/price.txt', 'r', encoding="utf-8").read(),
                   parse_mode = 'HTML')
    time.sleep(.5)
    ads_timetable_message(message)
    time.sleep(.5)
    bot.send_message(message.from_user.id,
                     text = open(f'{messages_folder}/contacts.txt', 'r', encoding="utf-8").read(),
                     parse_mode = 'HTML')
    time.sleep(0.5)
    bot.send_message(message.from_user.id,
                     text = open(f'{messages_folder}/ads_refer.txt', 'r', encoding="utf-8").read(),
                     parse_mode = 'HTML')
    logger.info(f'Карл дал информацию о рекламе {message.from_user.username}')

###   рекламное расписание   ###
@bot.message_handler(chat_types = ['private'], commands=['timetable'])
def ads_timetable_message(message):
    bot.send_message(backend_tg,
                     text = f"Юзер @{message.from_user.username} запросил рекламное расписание.")
    bot.send_message(message.from_user.id,
                     text = open(f'{messages_folder}/timetable.txt', 'r', encoding="utf-8").read(),
                     parse_mode = 'HTML')
    logger.info(f'Карл дал ссылку на расписание {message.from_user.username}')

    
bot.infinity_polling(timeout = 10, long_polling_timeout = 5)
