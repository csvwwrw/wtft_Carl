import telebot
import logging
import custom_lib.config as config
import custom_lib.logger_setup as logger_setup
import time

###   НАСТРОЙКА ЛОГГЕРА   ###
logger = logging.getLogger('')
    
logger_setup.double_logger_setup('carl_chatbot.log', 'carl_chatbot_error.log', logger = logger)

###   РЕГИСТРАЦИЯ БОТА   ###

bot = telebot.TeleBot(config.TG_TOKEN)

pinned_id_path = 'ids/pinned_id.txt'
with open(pinned_id_path, "r") as file:
        pinned_id = int(file.read())
        
###   приветствие в чате   ###
@bot.message_handler(content_types = ['new_chat_members'])
def rules_message(message):
    bot.send_photo(message.chat.id, open("messages/funballs.jpg", 'rb'))
    bot.reply_to(message,
                 f"""Приветствую, любитель некомфортных месседжей и несмешных шариков!
Добро пожаловать в чат wtf tumblr. Не пугайся, если попал сюда через комментарии - это наша антиспам-мера, можешь оставить комментарий и в любой момент выйти из чата, если тебе станет неуютно.
А в <a href = 'https://t.me/wtf_tumblr_chat/{pinned_id}'>закрепе</a> ты найдёшь правила, которые помогут сделать твоё пребывание в чате комфортным, а так же всяческие активности, подчаты и другую полезную информацию.""", parse_mode = 'HTML')
    logger.info(f'Карл поприветсвовал {message.from_user.username}')

###   приветствие в личных сообщениях   ###
@bot.message_handler(chat_types = ['private'], commands=['start', 'help'])
def start_message(message):
    bot.send_message(message.from_user.id,
                     """Приветствую, я - Карл, маскот канала @wtf_tumblr.
Информациюб о размещении рекламы в канале можно получить через команду /ads
Ссылку на актуальное расписание рекламных слотов можно получить через команду /timetable""", parse_mode = 'HTML')
    logger.info(f'Карл рассказал о себе {message.from_user.username}')

###   инфа о рекламе   ###
@bot.message_handler(chat_types = ['private'], commands=['ads'])
def ads_message(message):
    bot.send_message(191941411,
                     text = f"Юзер @{message.from_user.username} запросил информацию о рекламе.")
    bot.send_message(message.from_user.id, 
                     text = open('messages/rules.txt', 'r', encoding="utf-8").read(), 
                     parse_mode = 'HTML')
    time.sleep(.5)
    bot.send_photo(message.from_user.id,
                   open('messages/price.png', 'rb'),
                   caption = open('messages/price.txt', 'r', encoding="utf-8").read(),
                   parse_mode = 'HTML')
    time.sleep(.5)
    ads_timetable_message(message)
    time.sleep(.5)
    bot.send_message(message.from_user.id,
                     text = open('messages/contacts.txt', 'r', encoding="utf-8").read(),
                     parse_mode = 'HTML')
    time.sleep(0.5)
    bot.send_message(message.from_user.id,
                     text = "О рекламе в нашем <a href = 'https://vk.com/wtf_tumblr'>паблике в ВК</a> можно почитать <a href = 'https://vk.com/page-89397630_50525864'>тут</a>.",
                     parse_mode = 'HTML')
    logger.info(f'Карл дал информацию о рекламе {message.from_user.username}')

###   рекламное расписание   ###
@bot.message_handler(chat_types = ['private'], commands=['timetable'])
def ads_timetable_message(message):
    bot.send_message(191941411,
                     text = f"Юзер @{message.from_user.username} запросил рекламное расписание.")
    bot.send_message(message.from_user.id,
                     text = open('messages/timetable.txt', 'r', encoding="utf-8").read(),
                     parse_mode = 'HTML')
    logger.info(f'Карл дал ссылку на расписание {message.from_user.username}')

@bot.message_handler(func=lambda message: message.from_user.id == 191941411)
def to_chat_resend(message):
    if "МОДЕРКА" in message.text:
        response_text = message.text.replace('МОДЕРКА', '')
        bot.send_message(config.tg_chat,
                         text = response_text,
                         parse_mode = 'HTML')
    
bot.infinity_polling(timeout = 10, long_polling_timeout = 5)
