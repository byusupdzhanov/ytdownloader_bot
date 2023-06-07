import telebot
import yt_dlp
import os
from telebot import types
from config import bot_settings, img_src
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytiktok
import requests

bot = telebot.TeleBot(token=bot_settings['token'])


# список необходимых прав доступа к таблице
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# путь к файлу с ключами авторизации (получается при создании ключа доступа в консоли Google API)
creds = ServiceAccountCredentials.from_json_keyfile_name('googlesj.json', scope)
# идентификатор таблицы
sheet_id = '1x0zIOyz0jBol4kqyE4x36-x-L_vk7NRRD4pGbuwP_zY'
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).sheet1


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    row = [chat_id]
    sheet.append_row(row)
    bot.send_message(message.chat.id, 'Привет, ты находишься в главном меню, выбери действие✅'
                                      '\n\n'
                                      'Автор: @dontbesoseriouspls',
                     reply_markup=create_menu_keyboards())
    bot.register_next_step_handler(message, buttons_checker)


def create_menu_keyboards():
    menu_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    buttons = [
        types.KeyboardButton('Скачать видео с Youtube📺'),
        types.KeyboardButton('Скачать видео с TikTok🎵'),
        types.KeyboardButton('Скачать музыку с VK (в разработке)'),
    ]
    menu_keyboard.add(*buttons)
    return menu_keyboard


def media_download_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    video_button = types.KeyboardButton('Видео')
    audio_button = types.KeyboardButton('Аудио')
    back_button = types.KeyboardButton('Назад')
    keyboard.add(video_button, audio_button, back_button)
    return keyboard


def buttons_checker(message):
    text = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    butt = types.KeyboardButton('Назад')
    keyboard.add(butt)
    if text == 'Скачать видео с Youtube📺':
        bot.send_message(message.chat.id, 'Отлично, давай скачаем любое '
                                          'видео с <b>YouTube</b>📺. Поддерживаемые форматы:'
                                          '\n'
                                          'YouTube Video\n'
                                          'YouTube Shorts\n\n'
                                          'Отправь ссылку формата:\n'
                                          'https://youtube.com/watch?=xxxxxxxx\n'
                                          'https://youtube.com/shorts/xxxxxxxx'
                                          '\n\n'
                                          '<b>Внимание!</b> – пока что скачивание видео работает в тестовом режиме👨‍\n'
                                          'Действует ограничение на длительность <i>видео</i> – не более <b>4 мин</b>\n'
                                          'Ограничение на <i>аудио</i> – не более <b>15 мин</b>'
                                          '\n\n'
                                          'Приятного пользования ботом!\n\n'
                                          'Есть вопросы, идеи по улучшению функционала – '
                                          'пиши автору @dontbesoseriouspls ✅', parse_mode='html',
                         disable_web_page_preview=True)
        bot.register_next_step_handler(message, download_url_handler)

    elif text == 'Скачать видео с TikTok🎵':
        bot.send_message(message.chat.id, 'Супер! Отправь мне ссылку на видео в <b>TikTok</b>'
                         '\n\n'
                         'Ссылка ввида:'
                         '\n\n'
                         'https://vt.tiktok.com/xxxxxx',
                         parse_mode='html', disable_web_page_preview=True)
        bot.register_next_step_handler(message)

    elif text == 'Скачать музыку с VK (в разработке)':
        bot.send_photo(message.chat.id, photo=img_src['uc_photo'],
                       caption='Похоже ты забрел не туда\n'
                               'К сожалению, данный раздел находится в '
                               'разработке',
                       reply_markup=keyboard)
        bot.register_next_step_handler(message, buttons2_checker)
    else:
        bot.send_message(message.chat.id, 'Выбери правильное действие')
        bot.register_next_step_handler(message, buttons_checker)


def buttons2_checker(message):
    text = message.text
    if text == 'Назад':
        bot.register_next_step_handler(message, start_message)
    else:
        bot.send_message(message.chat.id, 'Укажите верное действие')
        bot.register_next_step_handler(message, buttons2_checker)


def download_url_handler(message):
    url = message.text
    download_youtube(message, url)


def download_youtube(message, url):
    bot.send_message(message.chat.id, 'Выберите формат загрузки:', reply_markup=media_download_buttons())
    bot.register_next_step_handler(message, download_format_handler, url)


def download_format_handler(message, url):
    format_choice = message.text.lower()
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton('Назад')
    keyboard.add(btn)
    if format_choice == 'видео':
        bot.send_message(message.chat.id, 'Идет скачивание видео, ожидайте...')
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption='Скачано при помощи @getsdownload_bot ✅',
                           reply_markup=keyboard)
            bot.register_next_step_handler(message, buttons2_checker)
        os.remove(filename)
    elif format_choice == 'аудио':
        bot.send_message(message.chat.id, 'Идет скачивание аудио, ожидайте...')
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best',
            'outtmpl': '%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
        with open(filename, 'rb') as f:
            bot.send_audio(message.chat.id, f, caption='Скачано при помощи @getsdownload_bot ✅',
                           reply_markup=keyboard)
            bot.register_next_step_handler(message, buttons2_checker)
        os.remove(filename)
    elif format_choice == 'назад':
        # handle back button press
        pass
        bot.register_next_step_handler(message, buttons2_checker)
    else:
        bot.send_message(message.chat.id, 'Выберите формат загрузки:', reply_markup=media_download_buttons())
        bot.register_next_step_handler(message, download_format_handler, url)

'''
def download_tt(message, video_url):
    response = requests.get(video_url)
    url = message.text
    tiktok = tiktok(url)
    with open
    '''



bot.polling()
