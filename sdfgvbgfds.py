from pytube import Playlist
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter
import asyncio
from pytube import YouTube, Playlist
import os
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from moviepy.editor import VideoFileClip
import re
import requests
import youtube_dl
import scrapetube
import sqlite3

bot = AsyncTeleBot(token='6071992423:AAETXoZ8tjsnyrZbO0iXTKnxgyqgdjhRGOg', state_storage=StateMemoryStorage())
#word = input('что хотите искать:')

#videos = scrapetube.get_search(word, limit=10)

#for video in videos:
    #print(f'https://www.youtube.com/watch?v={video["videoId"]}')

titles = []

conn = sqlite3.connect('bot_data.db')
c = conn.cursor()

# Создаем таблицу, если она еще не существует
c.execute('''CREATE TABLE IF NOT EXISTS video_data 
             (user_id INTEGER, title TEXT, link TEXT)''')


class States(StatesGroup):
    first = State()
    second = State()
    third = State()

class ProductsCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.chat.id, 'Привет, отправь ссылку на плейлист')
    await bot.set_state(message.from_user.id, States.first)


@bot.message_handler(state=States.first)
async def getting_link(message):
    link = message.text
    p = Playlist(link)
    try:
        await bot.send_message(message.chat.id, f'Downloading: {p.title}')
        for url in p.video_urls[:3]:
            await bot.send_message(message.chat.id, url)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['name'])
async def by_name(message):
    await bot.send_message(message.chat.id, 'Введите запрос:')
    await bot.set_state(message.from_user.id, States.second)


@bot.message_handler(state=States.second)
async def scrappin_by_name(message):
    nametag = message.text
    videos = scrapetube.get_search(nametag, limit=5)
    try:
        await bot.send_message(message.chat.id, 'Вот 5 результатов!')

        # Удаляем старые результаты для данного пользователя
        c.execute("DELETE FROM video_data WHERE user_id = ?", (message.from_user.id,))
        conn.commit()

        for video in videos:
            link = f'https://www.youtube.com/watch?v={video["videoId"]}'
            yt = YouTube(link)
            title = yt.title

            # Вставляем данные в таблицу
            c.execute("INSERT INTO video_data VALUES (?, ?, ?)",
                      (message.from_user.id, title, link))

        # Коммитим изменения в базе данных
        conn.commit()

        # Извлекаем данные из базы данных и формируем текст сообщения
        c.execute("SELECT rowid, title FROM video_data WHERE user_id = ?",
                  (message.from_user.id,))
        titles = [f'{row[0]}. {row[1]}' for row in c.fetchall()]

        message_text = '\n'.join(titles)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        for i in range(1, len(titles) + 1):
            callback_data = f'download_{i}'
            keyboard.add(types.InlineKeyboardButton(f'Скачать {i}', callback_data=callback_data))
        await bot.send_message(message.chat.id, text=message_text, reply_markup=keyboard, disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(message.chat.id, f'Произошла непредвиденная ошибка: {str(e)}')


@bot.callback_query_handler(func=lambda call: True)
async def callback_handler(call):
    if call.data.startswith('download_'):
        video_index = int(call.data.split('_')[1])

        # Получаем ссылку и название видео из базы данных
        c.execute("SELECT title, link FROM video_data WHERE user_id = ? AND rowid = ?",
                  (call.from_user.id, video_index))
        video_title, link = c.fetchone()

        youtube = YouTube(link)
        await bot.send_message(call.message.chat.id, f'Скачиваю вот это вот --> {link}')
        await bot.send_message(call.from_user.id, 'Уже работаю над этим\n <b>Бип буп бип</b>', parse_mode='html')
        try:
            video = youtube.streams.filter(progressive=True, file_extension='mp4',
                                           res='720p').get_highest_resolution()
            filename = f'{video.default_filename}'
            video.download(output_path=os.getcwd(), filename=filename)
            video_clip = VideoFileClip(filename)
            width, height = video_clip.size
            video_clip.close()

            file_size = os.path.getsize(filename) / (1024 * 1024)  # Размер файла в МБ
            views = youtube.views
            author = youtube.author
            max_caption_length = 300
            formatted_views = "{:,}".format(views).replace(",", " ")

            if len(video_title) > max_caption_length:
                video_title = video_title[:max_caption_length] + '...'  # Ограничение длины названия

            if file_size <= 50:
                with open(filename, 'rb') as f:
                    await bot.send_video(call.from_user.id, f,
                                         caption=f'\nСкачано при помощи @getsdownload_bot ✅',
                                         width=width, height=height, parse_mode='html',
                                         )

            else:
                await bot.send_message(call.from_user.id, text='дохуя весит',
                                       parse_mode='html')

            # Удаляем данные из базы данных после скачивания видео
            c.execute("DELETE FROM video_data WHERE user_id = ? AND rowid = ?",
                      (call.from_user.id, video_index))
            conn.commit()

            os.remove(filename)

        except Exception as e:
            if 'age restricted' in str(e):
                await bot.send_message(call.from_user.id, text=str(e),
                                       parse_mode='html')
            elif 'object has no attribute' in str(e):
                await bot.send_message(call.from_user.id, text=str(e),
                                       parse_mode='html')
                await bot.send_message(chat_id='-1001879360469', text=str(e))
            else:
                await bot.send_message(call.from_user.id, f'Непредвиденная ошибка: {str(e)}',
                                       )
                await bot.send_message(chat_id='-1001879360469', text=str(e))


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(ProductsCallbackFilter())

asyncio.run(bot.polling(non_stop=True))

#https://www.youtube.com/list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n