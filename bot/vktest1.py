import os
import time

import telebot
import youtube_dl
import requests
from telebot import types
import re

bot_token = '5990163436:AAGXxv5Cw2m2QYKtdL1JgdBNUCfxkcj4mxE'
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(text='Привет! Здесь ты можешь скачать Видео и Клипы VK  ! Напиши /vk',chat_id=message.chat.id)

@bot.message_handler(commands=['vk'])
def handle_vk_command(message):
    bot.send_message(message.chat.id, 'Введите ссылку на видео следующего вида \nhttps://vk.com/video-xxxxxxxx_xxxxxxxx:\nhttps://vk.com/clip-xxxxxxxxx_xxxxxxxx')
    bot.register_next_step_handler(message, process_vk_video)





def process_vk_video(message):
    try:
        def downloadsend(video_url, message, token, owner_id):
            print(video_url)
            video_get_url = f"https://api.vk.com/method/video.get?owner_id={owner_id}&videos={video_url}&access_token={token}&v=5.81"
            req = requests.get(video_get_url).json()
            print(req)
            response=req["response"]
            items=response['items'][0]
            descript = items['description']
            duration = items['duration']
            views =items['views']
            widthvideo = items['width']
            heightvideo = items['height']

            url = items['player']

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_filename = ydl.prepare_filename(info_dict)
                with open(video_filename, 'rb') as video_file:
                    video_size = os.path.getsize(video_filename)
                    max_video_size = 50 * 1024 * 1024  # 50 МБ (максимальный размер видео в Telegram)
                    if video_size > max_video_size:
                        bot.send_message(chat_id=message.chat.id,
                                         text='Видео слишком большое. Пожалуйста, выберите другое видео.')
                    else:
                        bot.send_video(chat_id=message.chat.id, video=video_file, duration=int(duration),supports_streaming=True,width=int(widthvideo),   height=int(heightvideo))
                        time.sleep(20)
                        os.remove(video_filename)

        video_url = message.text
        token = 'vk1.a.hiOC4NAoKCFp5o0qFrNKd7xb_xzJTV2-85PGbe3-YYXb61ySGOOUSUPYqjwdtrzo6m9Wd-XQ3nN0MDzGx8Wvqre0QAR2mMUjtlapw6t83q8EHv81GXNzcxX8Jx7AFqs94NKXg9pd4Gm6mT8DFTU5VfTpXs6a2YRPAgogkZtWkTyUUcpKgUD5gigBroEtPyhZbd5XAm7yR_8v8FyiAkPfbg'
        owner_id = '230352030'

        if 'https://vk.com/video-' in video_url:
            video_url = video_url[20:]

        elif 'https://vk.com/clip-' in video_url:
            video_url = video_url[19:]

        else:
            bot.send_message(message.chat.id, "Это не ссылка на видео VK.")
            return  handle_vk_command(message)
            pass
        if '?' in video_url :
                # Извлечение идентификатора видео VK
            video_url = video_url.split('?')[0]

        downloadsend(video_url,message,token,owner_id)



    except Exception as e:
        print(e)








bot.polling()