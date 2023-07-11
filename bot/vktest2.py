import os
import time
import string
import random
import telebot
import youtube_dl
import requests
from telebot import types
import re
import subprocess
from moviepy.editor import *

bot_token = '5990163436:AAGXxv5Cw2m2QYKtdL1JgdBNUCfxkcj4mxE'
bot = telebot.TeleBot(bot_token)

params = []


@bot.message_handler(commands=['start'])
def handle_start(message):
  bot.send_message(
    text='Привет! Здесь ты можешь скачать Видео и Клипы VK  ! Напиши /vk',
    chat_id=message.chat.id)


# @bot.message_handler(commands=['vk'])
# def handle_vk_command(message):
#   bot.send_message(
#     message.chat.id, 'Введите ссылку на видео следующего вида '
#     '\nhttps://vk.com/video-xxxxxxxx_xxxxxxxx:'
#     '\nhttps://vk.com/clip-xxxxxxxxx_xxxxxxxx')
#   bot.register_next_step_handler(message, process_vk_video)


@bot.message_handler(commands=['vk'])
def handle_vk_command(message):
  bot.send_message(
    message.chat.id, 'Введите ссылку на видео следующего вида '
    '\nhttps://vk.com/video-xxxxxxxx_xxxxxxxx:'
    '\nhttps://vk.com/clip-xxxxxxxxx_xxxxxxxx')
  bot.register_next_step_handler(message, process_vk_link)


def process_vk_link(message):
    link = message.text
    chat_id = message.chat.id
    params.append(link)
    # Здесь вы можете добавить проверку введенной ссылки и обработку ошибок, если необходимо

    # Создание объекта клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Добавление кнопок
    button_480 = types.KeyboardButton('480')
    button_360 = types.KeyboardButton('360')
    button_720 = types.KeyboardButton('720')
    keyboard.add(button_480, button_360,button_720)

    bot.send_message(chat_id, 'Выберите качество видео:', reply_markup=keyboard)
    bot.register_next_step_handler(message, process_vk_video)

def process_vk_video(message):
  try:
  
    def downloadsend(video_url, message, token, owner_id, quality):
      bot.send_message(chat_id=message.chat.id,text='Ожидайте скачивание видео')
      video_get_url = f"https://api.vk.com/method/video.get?owner_id={owner_id}&videos={video_url}" \
                      f"&access_token={token}&v=5.81"
      req = requests.get(video_get_url).json()
      response = req["response"]
      print(req)
      items = response['items'][0]
      if 'content_restricted_message' in items:
        bot.send_message(chat_id=message.chat.id, text='Видео недоступно изза приватности ')
        return handle_vk_command(message)
      duration = items['duration']
      # descr = items['description']
      
      widthvideo = items['width']
      heightvideo = items['height']
      url = items['player']

      # ydl_opts = {
      #   'format':
      #   'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
      #   'outtmpl':
      #   f'%(title)s_{video_url}.%(ext)s',
      #   'postprocessors': [{
      #     'key': 'FFmpegVideoConvertor',
      #     'preferedformat': 'mp4'
      #   }],
      #   'self_contained':
      #   True
      # }
      ydl_opts = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': f'%(title)s_{video_url}.%(ext)s',
    'self_contained': True
}

      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # info_dict = ydl.extract_info(url, download=True)
        # video_filename = ydl.prepare_filename(info_dict)
        # video_file_size = os.path.getsize(video_filename)
        # max_video_size = 50 * 1024 * 1024  # 50 МБ (максимальный размер видео в Telegram)

        # if video_file_size > max_video_size:
        #   bot.send_message(
        #     chat_id=message.chat.id,
        #     text=
        #     'Видео слишком большое. Скачайте вручную. Пожалуйста, выберите другое видео.'
        #   )
        #   bot.send_message(text=f'Ваша ссылка для скачивания видео {url}',
        #                    chat_id=message.chat.id)
        #   os.remove(video_filename)
        # else:
        info_dict = ydl.extract_info(url, download=True)
        video_filename = ydl.prepare_filename(info_dict)
        video_file_size = os.path.getsize(video_filename)
        print(video_file_size/1024/1024)
        video = VideoFileClip(video_filename)
        video_resized = video.resize(height=quality)
        # Изменение разрешения до 720p
        max_video_size = 50 * 1024 * 1024  # 50 МБ (максимальный размер видео в Telegram)
        video_resized.write_videofile('resized_video.mp4', codec='libx264')
        video_file_size = os.path.getsize('resized_video.mp4')
        print(video_file_size/1024/1024)
        os.remove(video_filename)
        if video_file_size < max_video_size:
          with open('resized_video.mp4', 'rb') as video_file:
            bot.send_video(chat_id=message.chat.id,
                           video=video_file,
                           caption='Скачано при помощи \n@getsdownload_bot',
                           duration=int(duration),
                           supports_streaming=True,
                           width=int(widthvideo),
                           height=int(heightvideo))
          params.clear()
          os.remove('resized_video.mp4')
        else:
          handle_vk_command(message)

    quality = int(message.text)
    print(quality)
    video_url = params[0]
    print(video_url)
    token = 'vk1.a.hiOC4NAoKCFp5o0qFrNKd7xb_xzJTV2-85PGbe3-YYXb61ySGOOUSUPYqjwdtrzo6m9Wd-XQ3nN0MDzGx8Wvqre0QAR2m' \
            'MUjtlapw6t83q8EHv81GXNzcxX8Jx7AFqs94NKXg9pd4Gm6mT8DFTU5VfTpXs6a2YRPAgogkZtWkTyUUcpKgUD5gigBroEtPyhZ' \
            'bd5XAm7yR_8v8FyiAkPfbg'
    owner_id = '230352030'

    if 'https://vk.com/video-' in video_url:
      video_url = video_url[20:]
    elif 'https://vk.com/video' in video_url and '-' not in video_url:
      video_url = video_url[20:]
    elif 'https://vk.com/clip-' in video_url:
      video_url = video_url[19:]
    elif 'https://vk.com/clip' in video_url and '-' not in video_url:
      video_url = video_url[19:]
    else:
      bot.send_message(message.chat.id, "Это не ссылка на видео VK.")
      return handle_vk_command(message)

    if '?' in video_url:
      video_url = video_url.split('?')[0]

    downloadsend(video_url, message, token, owner_id, quality)
  except Exception as e:
    print(e)


bot.polling()
