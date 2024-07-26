from vk_api import VkApi
import telebot
import youtube_dl
import os
import requests
import urllib
import time
import logging
import custom_lib.config as config
import custom_lib.logger_setup as logger_setup



###   НАСТРОЙКА ЛОГГЕРА   ###
logger = logging.getLogger('')
    
logger_setup.double_logger_setup('carl_parser.log', 'carl_parser_error.log', logger = logger)

###   КОФИГУРАЦИЯ   ###
tg_channel = config.tg_channel
tg_chat = config.tg_chat
vk_domain = config.vk_domain
alpha_domain = config.alpha_domain

last_id_path = 'ids/last_known_id.txt'
pinned_id_path = 'ids/pinned_id.txt'

blacklist = config.blacklist
time_sleep = config.time_sleep

###   ПОЛУЧЕНИЕ АПИ ВК И ТЕЛЕГИ   ###
vk_session = VkApi(token = config.VK_TOKEN, api_version = config.API_VERSION)
vk = vk_session.get_api()

bot = telebot.TeleBot(config.TG_TOKEN)

###   НАЧИНАЕМ КАРНАВАЛ   ###
while True:

###   ПОДГРУЗКА ПОСЛЕДНЕГО АЙПИ   ###
    with open(last_id_path, "r") as file:
            last_id = int(file.read())
    
    ###  ПОДГРУЖАЕМ ПОСЛЕДНИЕ 10 ПОСТОВ    ###
    try:
        posts = vk.wall.get(
            domain = vk_domain,
            count = 10
            )['items'][::-1]
        posts = posts[0:9]
        
        id_start = posts[0]['id']
        id_stop = posts[-1]['id']
        logger.info(f'Сканирую посты id:[{id_start} - {id_stop}]')
    except Exception as e:
        logger.info('ОШИБКА: СКАНИРОВАНИЕ')
        logger.error(e, exc_info = True)

    for post in posts:

        photo_list = []
        post_id = post['id']
        text_in_post = post['text']
        has_poll = False

###  ПРОВЕРЯЕМ ЭЛИДЖИБИЛИТИ ПОСТА    ###

###   ЕСЛИ ПОСТ ПОДХОДИТ   ###
        if int(post_id) > int(last_id):
            if alpha_domain not in text_in_post:
                logger.info(f'- Пост {post_id} пропущен (рекламный пост)')

            elif any(word in text_in_post for word in blacklist):
                logger.info( f'- Пост {post_id} пропущен (объявление)')

            else:
                logger.info(f'- Готовим пост {post_id}:')

    ###   СКАНИРУЕМ ВЛОЖЕНИЯ   ###
                for attachment in post['attachments']:

    ###   ЕСЛИ ЕСТЬ ВИДЕО, ОТПРАВЛЯЕМ ЕГО   ###
                    if attachment['type'] == 'video':
                        try:
                            owner = attachment['video']['owner_id']
                            video = attachment['video']['id']
                            key = attachment['video']['access_key']
                            video_data = vk.video.get(
                                access_token = config.VK_TOKEN,
                                v = config.API_VERSION,
                                videos = f'{owner}_{video}_{key}'
                                )['items'][0]
                            video_url = video_data['player']
                            video_title = video_data['title'] + '.mp4'
                            logger.info(f'\tСкачивается видео {video_title}')
                            ydl_opts = {
                                'outtmpl' : video_title,
                                'quiet' : True
                                }
                            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([video_url])
                            logger.info(f'\t Отправляется видео {video_title}')
                            bot.send_video(
                                chat_id = tg_channel,
                                video = open(video_title, 'rb'),
                                timeout = 500)
                            logger.info(f'\t Видео {video_title} отправлено. Удаляем.')
                            os.remove(video_title)
                        except Exception as e:
                            logger.info('ОШИБКА: ОТПРАВКА ВИДЕО')
                            logger.error(e, exc_info = True)
                            

    ###   ЕСЛИ ЕСТЬ АУДИО, ОТПРАВЛЯЕМ ЕГО   ###
                    elif attachment['type'] == 'audio':
                        try:
                            audio_url = attachment['audio']['url']
                            audio_title = attachment['audio']['title'] + '.mp3'
                            logger.info(f'\tСкачивается аудио {audio_title}')
                            audio = requests.get(audio_url)
                            with open(audio_title, 'wb') as f:
                                f.write(audio.content)
                            logger.info(f'\t Отправляется аудио {audio_title}')
                            bot.send_audio(
                                chat_id = tg_channel,
                                audio = open(audio_title, 'rb'))
                            logger.info(f'\t Аудио {audio_title} отправлено. Удаляем.')
                            os.remove(audio_title)
                        except Exception as e:
                            logger.info('ОШИБКА: ОТПРАВКА АУДИО')
                            logger.error(e, exc_info = True)

    ###   ЕСЛИ ЕСТЬ ДРУГОЕ ВЛОЖЕНИЕ (ОБЫЧНО ГИФКА), ОТПРАВЛЯЕМ ЕГО   ###
                    elif attachment['type'] == 'doc':
                        try:
                            doc_url = attachment['doc']['url']
                            doc_title = attachment['doc']['title'] + '.' + attachment['doc']['ext']
                            logger.info(f'\tСкачивается документ {doc_title}')
                            doc = requests.get(doc_url)
                            with open(doc_title, 'wb') as f:
                                f.write(doc.content)
                            logger.info(f'\t Отправляется документ {doc_title}')
                            bot.send_document(
                                chat_id = tg_channel,
                                document = open(doc_title, 'rb'))
                            logger.info(f'\t Документ {doc_title} отправлен. Удаляем.')
                            os.remove(doc_title)
                        except Exception as e:
                            logger.info('ОШИБКА: ОТПРАВКА ДОКУМЕНТА')
                            logger.error(e, exc_info = True)

    ###   ДЕЛАЕМ СПИСОК ФОТО В ПОСТЕ   ###
                    elif attachment['type'] == 'photo':
                        sizes = attachment['photo']['sizes']
                        height = []
                        for i in range(len(sizes)):
                            height.append(sizes[i]['height'])
                        photo_list.append(sizes[height.index(max(height))]['url'])
                        
    ###   ЗАПОМИНАЕМ ЧТО НУЖНО СДЕЛАТЬ ОПРОС   ###
                    elif attachment['type'] == 'poll':
                        has_poll = True
                        poll = attachment['poll']

    ###   ДЕЛАЕМ ИСТОЧНИК   ###
                    elif attachment['type'] == 'link':
                        logger.info('\tПолучаем источник из ссылки')
                        source = attachment['link']['url']
                        s = attachment['link']['title']

                    if 'copyright' in post:
                        logger.info('\tПолучаем источник из источника')
                        source = post['copyright']['link']
                        s = post['copyright']['name']
                        

    ###   ФОРМАТИРУЕМ ТЕКСТ ПОСТА   ###
                text_in_post = (f'{text_in_post}\nисточник: <a href="{source}">{s}</a>').replace(alpha_domain, '').replace('\n\n', '\n')
                logger.info(f'\tОтправляем пост {post_id}')

    ###   ОТПРАВЛЯЕМ ТЕКСТ И ФОТО, ЕСЛИ ОНО ОДНО   ###
                if len(photo_list) == 1:
                    try:
                        bot.send_photo(
                            tg_channel,
                            photo_list[0],
                            text_in_post,
                            parse_mode="HTML"
                            )
                    except Exception as e:
                        logger.info('ОШИБКА: ОТПРАВКА ФОТО')
                        logger.error(e, exc_info = True)

    ###   ОТПРАВЛЯЕМ ТЕКСТ И ФОТО, ЕСЛИ ИХ МНОГО   ###
                if len(photo_list) > 1:
                    try:
                        photo_file = []
                        for photo in photo_list:
                            photo_file.append(
                                telebot.types.InputMediaPhoto(urllib.request.urlopen(photo).read()))
                        photo_file[0].caption = text_in_post
                        photo_file[0].parse_mode = "HTML"
    
                        bot.send_media_group(
                            tg_channel,
                            photo_file
                            )
                    except Exception as e:
                        logger.info('ОШИБКА: ОТПРАВКА ГРУППЫ ФОТО')
                        logger.error(e, exc_info = True)
                    
    ###   ОТПРАВЛЯЕМ ОПРОС   ###
                if has_poll:
                    try:
                        bot.send_poll(chat_id = tg_channel,
                                      question = poll['question'],
                                      options = [i['text'] for i in poll['answers']],
                                      is_anonymous = poll['anonymous'],
                                      allows_multiple_answers = poll['multiple']
                                      )
                    except Exception as e:
                        logger.info('ОШИБКА: ОТПРАВКА ГРУППЫ ФОТО')
                        logger.error(e, exc_info = True)

                time.sleep(2)

    ###   СОХРАНЯЕМ НОВОЕ ПОСЛЕДНЕЕ АЙДИ ПОСТА   ###
                logger.info(f'\t!!! Пост {post_id} отправлен !!!')

            with open(last_id_path, "w") as file:
                file.write(str(post_id))

###   ОТПИНИВАЕМ ЦИКЛ   ###
    time.sleep(10)
    with open(pinned_id_path, "r") as file:
            pinned_id = int(file.read())
                            
    if bot.get_chat(tg_chat).pinned_message.message_id != pinned_id:
        while bot.get_chat(tg_chat).pinned_message.message_id != pinned_id:
            try:
                bot.unpin_chat_message(tg_chat)
                time.sleep(5)
                logger.info('Сообщения, отправленные за цикл, откреплены')
            except Exception as e:
                logging.info('ОШИБКА: ОТКРЕПЛЕНИЕ СООБЩЕНИЙ')
                logging.error(e, exc_info = True)


###   ОТПРАВЛЯЕМ БОТ СПАТЬ   ###
    with open(last_id_path, "r") as file:
            new_last_id = int(file.read())
    if new_last_id != last_id:
        logger.info(f'Новое last_id = {post_id}. Бот идёт спать.\n\n')
    else:
        logger.info('Новых сообщений нет. Бот идёт спать.\n\n')
    time.sleep(time_sleep)




























