from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter
import asyncio
from pytube import YouTube
import os
from telebot import types
from config import texts, img_src
from auth_data import bot_settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from moviepy.editor import VideoFileClip
import re
import requests
import youtube_dl
import scrapetube
import sqlite3

bot = AsyncTeleBot(token=bot_settings['test_token'], state_storage=StateMemoryStorage())

conn = sqlite3.connect('bot_data.db')
c = conn.cursor()

# Создаем таблицу, если она еще не существует
c.execute('''CREATE TABLE IF NOT EXISTS video_data 
             (user_id INTEGER, title TEXT, link TEXT)''')

# учет пользвателей в GSheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('googlesj.json', scope)
sheet_id = '1x0zIOyz0jBol4kqyE4x36-x-L_vk7NRRD4pGbuwP_zY'
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).sheet1

urls = {}
params = []
users_params = {}
titles = []

class MyStates(StatesGroup):
    obtainingUrl = State()
    MediaFormatChoosing = State()
    downloadHandler = State()
    mainMenu = State()
    vkDownloading = State()
    vkQualityHandler = State()
    ScrappingByName = State()

class ProductsCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


def backrepeat_keyboard():
    return types.InlineKeyboardMarkup(row_width=2,
                                      keyboard=[
                                          [
                                              types.InlineKeyboardButton(
                                                  text='В главное меню🔙',
                                                  callback_data='menu'
                                              ),
                                              types.InlineKeyboardButton(
                                                  text='Повтор🔁',
                                                  callback_data='repeat'
                                              )
                                          ]
                                      ]
                                      )
@bot.message_handler(commands=['start'])
async def start_message(message):
    chat_id = message.chat.id
    row = [chat_id]
    sheet.append_row(row)
    await bot.send_message(message.chat.id, text=texts['startMsgText'], parse_mode='html')


@bot.message_handler(commands=['vk'])
async def handle_vk_command(message):
    await bot.send_message(message.chat.id, text=texts['vk_start_text'], parse_mode='html')
    await bot.set_state(message.from_user.id, MyStates.vkQualityHandler, message.chat.id)


@bot.message_handler(state=MyStates.vkQualityHandler)
async def process_vk_link(message):
    link = message.text
    chat_id = message.chat.id
    params.append(link)
    # Здесь вы можете добавить проверку введенной ссылки и обработку ошибок, если необходимо

    # Создание объекта клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # Добавление кнопок
    button_480 = types.KeyboardButton('480')
    button_360 = types.KeyboardButton('360')
    button_720 = types.KeyboardButton('720')
    keyboard.add(button_480, button_360, button_720)

    await bot.send_message(chat_id, 'На данный момент, возможна загрузка только видео🙃\n\n'
                                    'Выберите качество загружаемого видео📹:', reply_markup=keyboard)
    await bot.set_state(message.from_user.id, MyStates.vkDownloading, message.chat.id)







@bot.message_handler(state=MyStates.vkDownloading)
async def process_vk_video(message):
    try:
        async def downloadsend(video_url, message, token, owner_id, quality):
            await bot.send_message(chat_id=message.chat.id, text='Идет скачивание, ожидайте')
            video_get_url = f"https://api.vk.com/method/video.get?owner_id={owner_id}&videos={video_url}" \
                            f"&access_token={token}&v=5.81"
            req = requests.get(video_get_url).json()
            response = req["response"]
            items = response['items'][0]
            if 'content_restricted_message' in items:
                await bot.send_message(chat_id=message.chat.id, text=texts['age_error'])
                return handle_vk_command(message)
            duration = items['duration']

            widthvideo = items['width']
            heightvideo = items['height']
            url = items['player']
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': f'%(title)s_{video_url}.%(ext)s',
                'self_contained': True
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_filename = ydl.prepare_filename(info_dict)
                video_file_size = os.path.getsize(video_filename)
                video = VideoFileClip(video_filename)
                video_resized = video.resize(height=quality)
                # Изменение разрешения до 720p
                max_video_size = 50 * 1024 * 1024  # 50 МБ (максимальный размер видео в Telegram)
                video_resized.write_videofile('resized_video.mp4', codec='libx264')
                video_file_size = os.path.getsize('resized_video.mp4')
                os.remove(video_filename)
                if video_file_size < max_video_size:
                    with open('resized_video.mp4', 'rb') as video_file:
                        await bot.send_video(chat_id=message.chat.id,
                                       video=video_file,
                                       caption='Скачано при помощи \n@getsdownload_bot ✅',
                                       duration=int(duration),
                                       supports_streaming=True,
                                       width=int(widthvideo),
                                       height=int(heightvideo))
                    params.clear()
                    os.remove('resized_video.mp4')
                else:
                    await bot.send_message(message.chat.id, text=texts['limitation_text_with_q'],
                                           parse_mode='html')
                    await handle_vk_command(message)

        quality = int(message.text)
        video_url = params[0]
        token = bot_settings['vk_token']
        owner_id = bot_settings['vk_owner_id']

        if 'https://vk.com/video-' in video_url:
            video_url = video_url[20:]
        elif 'https://vk.com/video' in video_url and '-' not in video_url:
            video_url = video_url[20:]
        elif 'https://vk.com/clip-' in video_url:
            video_url = video_url[19:]
        elif 'https://vk.com/clip' in video_url and '-' not in video_url:
            video_url = video_url[19:]
        else:
            await bot.send_message(message.chat.id, "Это не ссылка на видео VK.")
            return handle_vk_command(message)

        if '?' in video_url:
            video_url = video_url.split('?')[0]

        await downloadsend(video_url, message, token, owner_id, quality)
    except Exception as e:
        await bot.send_message(message.chat.id, f'Произошла непредвиденная ошибка: {str(e)}')
        await bot.send_message(chat_id='-1001879360469', text=str(e))


@bot.message_handler(commands=['tiktok'])
async def tt_first_msg(message):
    await bot.send_photo(message.chat.id, photo=img_src['uc_photo'], caption=texts['notready'], parse_mode='html')


@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, text=texts['help_text'], parse_mode='html', disable_web_page_preview=True)


@bot.message_handler(commands=['youtube'])
async def youtube_first_msg(message):
    await bot.send_message(message.chat.id, text=texts['youtubeFirstMsg'], parse_mode='html',
                           disable_web_page_preview=True)
    await bot.set_state(message.from_user.id, MyStates.obtainingUrl, message.chat.id)


@bot.message_handler(state=MyStates.obtainingUrl)
async def obtaining_url(message):
    url = message.text
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    match = re.search(pattern, url)
    if match:
        urls[message.chat.id] = {'youtube': url}
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        buttons = [
            types.KeyboardButton('Видео👾'),
            types.KeyboardButton('Аудио🎵')
        ]
        keyboard.add(*buttons)
        await bot.send_message(message.chat.id, text=texts['youtubeFormatType'], parse_mode='html',
                               reply_markup=keyboard)
        await bot.set_state(message.from_user.id, MyStates.downloadHandler, message.chat.id)
    else:
        await bot.send_message(message.chat.id, 'Сообщение не является ссылкой! Отправьте ссылку')
        await bot.set_state(message.from_user.id, MyStates.obtainingUrl, message.chat.id)


@bot.message_handler(state=MyStates.downloadHandler)
async def youtube_media_downloading(message):
    text = message.text
    url = urls[message.chat.id]['youtube']
    if text == 'Видео👾':
        await bot.send_message(message.chat.id, 'Идет скачивание, ожидайте')
        youtube = YouTube(url)
        try:
            video = youtube.streams.filter(progressive=True, file_extension='mp4',
                                           res='720p').get_highest_resolution()
            filename = f'{video.default_filename}'
            video.download(output_path=os.getcwd(), filename=filename)
            video_clip = VideoFileClip(filename)
            width, height = video_clip.size
            video_clip.close()

            file_size = os.path.getsize(filename) / (1024 * 1024)  # Размер файла в МБ
            video_title = youtube.title
            max_caption_length = 300

            if len(video_title) > max_caption_length:
                video_title = video_title[:max_caption_length] + '...'  # Ограничение длины названия

            if file_size <= 50:
                with open(filename, 'rb') as f:
                    await bot.send_video(message.chat.id, f,
                                         caption=f'<b>{video_title}</b>\n\n'
                                                 f'Скачано при помощи @getsdownload_bot ✅',
                                         width=width, height=height, parse_mode='html',
                                         reply_markup=backrepeat_keyboard())
            else:
                await bot.send_message(message.chat.id, text=texts['limitation_text'],
                                       parse_mode='html', reply_markup=backrepeat_keyboard())

            os.remove(filename)

        except Exception as e:
            if 'age restricted' in str(e):
                await bot.send_message(message.chat.id, text=texts['age_error'],
                                       reply_markup=backrepeat_keyboard(), parse_mode='html')
            elif 'object has no attribute' in str(e):
                await bot.send_message(message.chat.id, text=texts['error'],
                                       reply_markup=backrepeat_keyboard(), parse_mode='html')
                await bot.send_message(chat_id='-1001879360469', text=str(e))
            else:
                await bot.send_message(message.chat.id, f'Непредвиденная ошибка: {str(e)}',
                                       reply_markup=backrepeat_keyboard())
                await bot.send_message(chat_id='-1001879360469', text=str(e))
    elif text == 'Аудио🎵':
        await bot.send_message(message.chat.id, 'Идет скачивание, ожидайте!')
        youtube = YouTube(url)

        try:
            audio = youtube.streams.filter(only_audio=True).first()
            filename = f'{audio.default_filename}'
            audio.download(output_path=os.getcwd(), filename=filename)
            with open(filename, 'rb') as f:
                await bot.send_audio(message.chat.id, f, caption=f'Скачано при помощи @getsdownload_bot ✅',
                                     reply_markup=backrepeat_keyboard())
            os.remove(filename)
        except Exception as e:
            if 'age restricted' in str(e):
                await bot.send_message(message.chat.id, text=texts['age_error'],
                                       reply_markup=backrepeat_keyboard(), parse_mode='html')
            elif 'object has no attribute' in str(e):
                await bot.send_message(message.chat.id, text=texts['error'],
                                       reply_markup=backrepeat_keyboard(), parse_mode='html')
            else:
                await bot.send_message(message.chat.id, f'Непредвиденная ошибка: {str(e)}',
                                       reply_markup=backrepeat_keyboard())
                await bot.send_message(chat_id='-1001879360469', text=str(e))
        # os.remove(filename)

@bot.message_handler(commands=['search'])
async def by_name(message):
    await bot.send_message(message.chat.id, text=texts['search_text'], parse_mode='html')
    await bot.set_state(message.from_user.id, MyStates.ScrappingByName)


@bot.message_handler(state=MyStates.ScrappingByName)
async def scrappin_by_name(message):
    nametag = message.text
    videos = scrapetube.get_search(nametag, limit=5)
    try:
        await bot.send_message(message.chat.id, 'Вот 5 результатов👇\n'
                                                'Выбери подходящее, по названию, видео и скачивай🙂')

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

        # Извлекаем данные из базы данных, формируем текст сообщения и создаем кнопки
        message_text = ''
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        c.execute("SELECT rowid, title FROM video_data WHERE user_id = ?", (message.from_user.id,))

        for i, row in enumerate(c.fetchall(), start=1):
            message_text += f'{row[0]}. {row[1]}\n'
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
        await bot.send_message(call.message.chat.id, f'Идет скачивание данного видео: <a href="{link}">тык</a>',
                               parse_mode='html')
        await bot.send_message(call.from_user.id, 'Уже работаю над этим\n<b>Бип буп бип</b>⚙️', parse_mode='html')
        try:
            video = youtube.streams.filter(progressive=True, file_extension='mp4',
                                           res='720p').get_highest_resolution()
            filename = f'{video.default_filename}'
            video.download(output_path=os.getcwd(), filename=filename)
            video_clip = VideoFileClip(filename)
            width, height = video_clip.size
            video_clip.close()

            file_size = os.path.getsize(filename) / (1024 * 1024)  # Размер файла в МБ
            video_title = youtube.title
            max_caption_length = 300
            if len(video_title) > max_caption_length:
                video_title = video_title[:max_caption_length] + '...'  # Ограничение длины названия

            if file_size <= 50:
                with open(filename, 'rb') as f:
                    await bot.send_video(call.from_user.id, f,
                                         caption=f'<b>{video_title}</b>\n\n'
                                                 f'Скачано при помощи @getsdownload_bot ✅',
                                         width=width, height=height, parse_mode='html',
                                         reply_markup=backrepeat_keyboard())

            else:
                await bot.send_message(call.from_user.id, text=texts['limitation_text'],
                                       parse_mode='html', reply_markup=backrepeat_keyboard())

            # Удаляем данные из базы данных после скачивания видео
            c.execute("DELETE FROM video_data WHERE user_id = ? AND rowid = ?",
                      (call.from_user.id, video_index))
            conn.commit()

            os.remove(filename)

        except Exception as e:
            if 'age restricted' in str(e):
                await bot.send_message(call.from_user.id, text=texts['age_error'],
                                       parse_mode='html', reply_markup=backrepeat_keyboard())
            elif 'object has no attribute' in str(e):
                await bot.send_message(call.from_user.id, text=texts['error'],
                                       parse_mode='html', reply_markup=backrepeat_keyboard())
                await bot.send_message(chat_id='-1001879360469', text=str(e))
            else:
                await bot.send_message(call.from_user.id, f'Непредвиденная ошибка: {str(e)}',
                                       reply_markup=backrepeat_keyboard())
                await bot.send_message(chat_id='-1001879360469', text=str(e))

            os.remove(filename)

    elif call.data == 'users_count':
            user_ids = sheet.col_values(1)
            user_quantity = len(user_ids)
            await bot.send_message(call.from_user.id, f'Сейчас у бота насчитывается: {user_quantity} пользователей')
    elif call.data == 'menu':
        await bot.send_message(call.from_user.id, text=texts['startMsgText'], parse_mode='html')
    elif call.data == 'repeat':
        await bot.send_message(call.from_user.id, 'Отправь мне новую ссылку🧐')
        await bot.set_state(call.from_user.id, MyStates.obtainingUrl)
    elif call.data == 'users_ban':
        user_ids = sheet.col_values(1)
        for i in user_ids:
            await bot.send_message(call.from_user.id, f'{i}', )


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(ProductsCallbackFilter())

asyncio.run(bot.polling(non_stop=True))
