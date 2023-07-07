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
from configt import texts, img_src
from auth_data import bot_settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from moviepy.editor import VideoFileClip
import re

bot = AsyncTeleBot(token=bot_settings['test_token'], state_storage=StateMemoryStorage())

# учет пользвателей в GSheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/Users/bogdanyusupdjanov/Projects/tg-bot-downloader/test-space/googlesj.json', scope)
sheet_id = '1x0zIOyz0jBol4kqyE4x36-x-L_vk7NRRD4pGbuwP_zY'
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).sheet1

urls = {}
quality = {}
videotype = {}


admins = [169546656, 4444]


class MyStates(StatesGroup):
    obtainingUrl = State()
    MediaFormatChoosing = State()
    downloadHandler = State()
    mainMenu = State()
    playlistDownloader = State()
    qualityHandler = State()
    additionalHandler = State()


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


def quality_keyboard():
    return types.InlineKeyboardMarkup(row_width=2,
                                      keyboard=[
                                          [
                                              types.InlineKeyboardButton(
                                                  text='720p',
                                                  callback_data='720'
                                              ),
                                              types.InlineKeyboardButton(
                                                  text='480p',
                                                  callback_data='480'
                                              ),
                                              types.InlineKeyboardButton(
                                                  text='360p',
                                                  callback_data='360'
                                              ),
                                              types.InlineKeyboardButton(
                                                  text='240p',
                                                  callback_data='240'
                                              ),
                                              types.InlineKeyboardButton(
                                                  text='144p',
                                                  callback_data='144'
                                              ),
                                          ]
                                      ]
                                      )


def admin_keyboard():
    return types.InlineKeyboardMarkup(row_width=2,
                                      keyboard= [
                                          [
                                              types.InlineKeyboardButton(
                                                  text='Количество пользователей🔢',
                                                  callback_data='users_count'
                                              ),
                                              types.InlineKeyboardButton(
                                                  text='Заблокировать пользователя🚫',
                                                  callback_data='user_ban'
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


@bot.message_handler(commands=['admin'])
async def admin_panel(message):
    user_id = message.from_user.id

    if user_id in admins:
        await bot.send_message(message.chat.id, 'Добро пожаловать Администратор!')
        import time
        time.sleep(5)
        await bot.send_message(message.chat.id, 'Выбери действие (пока что доступно только 2):',
                               reply_markup=admin_keyboard())
    else:
        await bot.send_message(message.chat.id, 'Ты не являешься администратором! Вернись в меню!')


@bot.message_handler(commands=['vk'])
async def vk_first_msg(message):
    await bot.send_photo(message.chat.id, photo=img_src['uc_photo'], caption=texts['notready'], parse_mode='html')


@bot.message_handler(commands=['tiktok'])
async def tt_first_msg(message):
    await bot.send_photo(message.chat.id, photo=img_src['uc_photo'], caption=texts['notready'], parse_mode='html')


@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, text=texts['help_text'], parse_mode='html')


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

@bot.message_handler(state=MyStates.qualityHandler)
async def quality_handler(message):
    text = message.text
    if text == 'Видео👾':
        videotype[message.chat.id] = {'type': 'video'}
        await bot.send_message(message.chat.id, 'Выбери качество загружаемого видео:', reply_markup=quality_keyboard())
    elif text == 'Аудио🎵':
        videotype[message.chat.id] = {'type': 'audio'}
        await bot.set_state(message.from_user.id, MyStates.downloadHandler)


@bot.message_handler(state=MyStates.downloadHandler)
async def youtube_media_downloading(message):
    url = urls[message.chat.id]['youtube']
    media_type = videotype[message.chat.id]['type']
    async with bot.retrieve_data(message.from_user.id) as data:
        res = data['quality']
    if media_type == 'video':
        await bot.send_message(message.chat.id, 'Идет скачивание, ожидайте')
        youtube = YouTube(url)
        try:
            video = youtube.streams.filter(progressive=True, file_extension='mp4',
                                           res=res).get_highest_resolution()
            filename = f'{video.default_filename}'
            video.download(output_path=os.getcwd(), filename=filename)
            video_clip = VideoFileClip(filename)
            width, height = video_clip.size
            video_clip.close()

            file_size = os.path.getsize(filename) / (1024 * 1024)  # Размер файла в МБ
            video_title = youtube.title
            views = youtube.views
            rating = youtube.rating
            author = youtube.author
            max_caption_length = 300
            formatted_views = "{:,}".format(views).replace(",", " ")

            if len(video_title) > max_caption_length:
                video_title = video_title[:max_caption_length] + '...'  # Ограничение длины названия

            if file_size <= 50:
                with open(filename, 'rb') as f:
                    await bot.send_video(message.chat.id, f,
                                         caption=f'<b>{video_title}</b>'
                                                 f'\n\n'
                                                 f'Просмотры👀: {formatted_views} | Рейтинг📈: {rating} | '
                                                 f'Канал✍️: {author}'
                                                 f'\n\n'
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
            else:
                await bot.send_message(message.chat.id, f'Непредвиденная ошибка: {str(e)}',
                                       reply_markup=backrepeat_keyboard())
    elif media_type == 'audio':
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
            await bot.send_message(message.chat.id, f"Произошла непредвиденная ошибка:\n{str(e)}",
                                   reply_markup=backrepeat_keyboard())
        # os.remove(filename)


@bot.message_handler(commands=['youtube_playlist'])
async def playlist(message):
    await bot.send_message(message.chat.id, 'Отправь ссылку на плейлист!',)
    await bot.set_state(message.from_user.id, MyStates.playlistDownloader, message.chat.id)

@bot.message_handler(state=MyStates.playlistDownloader)
async def playlist_downloading(message):
    url = message.text
    p = Playlist(url)
    await bot.send_message(message.chat.id, f'Идет скачивание {p.title}, ожидайте!')
    for video in p.videos:
        filename = f'{video.description}'
        video.streams.first().download(output_path=os.getcwd(), filename=filename)

        with open(filename, 'rb') as f:
            await bot.send_video(message.chat.id, f,
                                 caption=f'ттттт')

@bot.callback_query_handler(func=lambda c: c.data == 'menu')
async def menu_callback(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, text=texts['startMsgText'], parse_mode='html')


@bot.callback_query_handler(func=lambda c: c.data == 'repeat')
async def menu_callback(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отправь мне новую ссылку🧐')
    await bot.set_state(call.from_user.id, MyStates.obtainingUrl)


@bot.callback_query_handler(func=lambda c: c.data == 'users_count')
async def users_counter(call: types.CallbackQuery):
    user_ids = sheet.col_values(1)
    user_quantity = len(user_ids)
    await bot.send_message(call.from_user.id,  f'Сейчас у бота насчитывается: {user_quantity} пользователей')


@bot.callback_query_handler(func=lambda c: c.data == 'user_ban')
async def users_counter(call: types.CallbackQuery):
    user_ids = sheet.col_values(1)
    for i in user_ids:
        await bot.send_message(call.from_user.id, f'{i}',)

@bot.callback_query_handler(func=lambda c: c.data == '720')
async def quality_720(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отлично, скачаем видео в качестве: <b>720p</b>', parse_mode='html')
    await bot.set_state(call.from_user.id, MyStates.downloadHandler)
    async with bot.retrieve_data(call.from_user.id) as data:
        data['quality'] = '720p'

@bot.callback_query_handler(func=lambda c: c.data == '480')
async def quality_480(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отлично, скачаем видео в качестве: <b>480p</b>', parse_mode='html')
    await bot.set_state(call.from_user.id, MyStates.downloadHandler)
    async with bot.retrieve_data(call.from_user.id) as data:
        data['quality'] = '480p'

@bot.callback_query_handler(func=lambda c: c.data == '360')
async def quality_360(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отлично, скачаем видео в качестве: <b>360p</b>', parse_mode='html')
    await bot.set_state(call.from_user.id, MyStates.downloadHandler)
    async with bot.retrieve_data(call.from_user.id) as data:
        data['quality'] = '360p'

@bot.callback_query_handler(func=lambda c: c.data == '240')
async def quality_240(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отлично, скачаем видео в качестве: <b>240p</b>', parse_mode='html')
    await bot.set_state(call.from_user.id, MyStates.downloadHandler)
    async with bot.retrieve_data(call.from_user.id) as data:
        data['quality'] = '240p'

@bot.callback_query_handler(func=lambda c: c.data == '144')
async def quality_144(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, 'Отлично, скачаем видео в качестве: <b>144p</b>', parse_mode='html')
    await bot.set_state(call.from_user.id, MyStates.downloadHandler)
    async with bot.retrieve_data(call.from_user.id) as data:
        data['quality'] = '144p'



bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(ProductsCallbackFilter())

asyncio.run(bot.polling(none_stop=True))
