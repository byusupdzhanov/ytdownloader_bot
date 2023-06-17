from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters, custom_filters
from telebot.asyncio_handler_backends import State, StatesGroup
import asyncio
import os, re, requests
import urllib.request
from tiktok import getCookie, getDownloadUrl, getDownloadID, getStatus


bot = AsyncTeleBot(token='6071992423:AAETXoZ8tjsnyrZbO0iXTKnxgyqgdjhRGOg')


class MyStates(StatesGroup):
    downloading = State()

def download_video(video_url, name):
    r = requests.get(video_url, allow_redirects=True)
    content_type = r.headers.get('content-type')
    if content_type == 'video/mp4':
        open(f'./videos/video{name}.mp4', 'wb').write(r.content)
    else:
        pass

@bot.message_handler(commands=['start'])
async def start_message(message):
    await bot.send_message(message.chat.id, 'Send me TikTok URL')
    await bot.set_state(message.from_user.id, MyStates.downloading, message.chat.id)


@bot.message_handler(state=MyStates.downloading)
async def downloading_video(message):
    if message.text.startswith('https://www.tiktok.com'):
        video_url = message.text
        cookie = getCookie()
        status = getStatus(video_url, cookie)
        if status == False:
            await bot.send_message(message.chat.id, 'Inccorect URL')
        else:
            await bot.send_message(chat_id=message.chat.id, parse_mode='HTML', text='<b>😎 Всё отлично.</b>Я получил ссылку и вижу видеоролик, мои шестёренки уже крутятся.\nЖди, скоро отправлю.')
            url = getDownloadUrl(video_url, cookie)
            video_id = getDownloadID(video_url, cookie)
            download_video(url, video_id)
            path = f'./videos/video{video_id}.mp4'
            with open(f'./videos/video{video_id}.mp4', 'rb') as file:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=file,
                    caption='Лови ролик, я красавчик? 😎'
                    )
            os.remove(path)
    elif message.text.startswith('https://vm.tiktok.com'):
        video_url = message.text
        req = urllib.request.Request(video_url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
            }
                    )
        url_v = urllib.request.urlopen(req).geturl()
        if url_v == 'https://www.tiktok.com/':
            await bot.send_message(chat_id=message.chat.id, parse_mode='HTML', text='Я не могу увидеть видео по ссылке, его или удалили, или я получил от тебя неправильную ссылку.<b>\n\nПроверь ещё раз и отправь мне.</b>')
        else:
            cookie = getCookie()
            await bot.send_message(chat_id=message.chat.id, parse_mode='HTML', text='<b>Жди, скоро отправлю!</b>')
            url = getDownloadUrl(url_v, cookie)
            video_id = getDownloadID(url_v, cookie)
            download_video(url, video_id)
            path = f'./videos/video{video_id}.mp4'
            with open(f'./videos/video{video_id}.mp4', 'rb') as file:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=file,
                    caption='Держи видео🚀'
                    )
            os.remove(path)
    else:
        await bot.send_message(chat_id=message.chat.id, parse_mode='HTML', text='<b>Мне нужна ссылка на Tik Tok видео, другие пока не умею скачивать.</b>')


bot.add_custom_filter(asyncio_filters.StateFilter(bot))

asyncio.run(bot.polling())
