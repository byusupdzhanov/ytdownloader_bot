bot_settings = {
    'token': 'your_tg_token',
    'test_token': 'xxxx',
    'api_id': 'tg_app',
    'api_hash': 'a',
}

img_src = {
    'uc_photo': 'https://s503sas.storage.yandex.net/rdisk/3b7352c1130fd38ace2251803803d1b31be892077b62370781ac087f92206'
                '7c7/64163b5e/xAT9F320_wuTumXz8U_X7jHrNV7ehMUt8EKYdUM836HPY3vk2vz1kmdCoXYHHATK1ONMCwXCb4JIHtP49FgMkg==?'
                'uid=797670624&filename=under-construction-sign-with-hat-on-traffic-cone-vector.webp&disposition=inline'
                '&hash=&limit=0&content_type=image%2Fwebp&owner_uid=797670624&fsize=59546&hid=7ca551be38cede32b02383b17'
                '2daf8f4&media_type=image&tknv=v2&etag=0db69dc6f99ecfa69708a30ea7df72c1&rtoken=1Zs5VB17M0ZL&'
                'force_default=yes&ycrid=na-1103900fb49c2b82ab663dd8fd7b65b6-downloader7e&ts=5f7343b5f1380&s='
                '5573e9786b94823ec39be029a36c0acaf37e1f1b15f43d243f75164e0a13e70e&pb=U2FsdGVkX19mUz88pKLAarRBc3f_'
                'wsvc3l5fwS4v1m8E3LbV_SR4o16JtAPPZB18o6yXXAJlEN2IQYM2LSKdBiMX3usg4r1C-mV9I3xpPU8',
}

texts = {
    'startMsgText': f'Привет! Я - бот для скачивания медиа с различных платформ!'
                    f'\n'
                    f'<b>Что я умею?</b>\n'
                    f'На данный момент, я нахожусь на этапе разработки, поэтому функционал ограничен '
                    f'только медиа с Youtube✅\n'
                    f'<b>Не отчаивайтесь!</b> В скором времени будет реализовано скачивание с VK и TikTok🤩\n'
                    f'Вот список комманд:\n'
                    f'/youtube - для скачивания с YouTube\n'
                    f'/vk - для скачивания с VK (в разработке)\n'
                    f'/tiktok - для скачивания с TikTok (в разработке)\n\n'
                    f'Для продолжения тыкайте на подходящую команду😇',

    'youtubeFormatType': f'<b>Отлично!</b>'
                         f' Для продолжения выбери формат скачивания:\n',

    'youtubeFirstMsg': 'Отлично, давай скачаем любое '
                       'видео с <b>YouTube</b>📺. Поддерживаемые форматы:'
                       '\n'
                       'YouTube Video\n'
                       'YouTube Shorts\n\n'
                       'Отправь ссылку формата:\n'
                       'https://youtube.com/watch?=xxxxxxxx\n'
                       'https://youtube.com/shorts/xxxxxxxx'
                       '\n\n'
                       '<b>Внимание!</b> – так как бот находится в разработке, действует ограничение\n'
                       ' по объему загружаемого файла - не более <b>50 Мб</b>🥲\n'
                       '\n\n'
                       'Приятного пользования ботом!\n\n'
                       'Есть вопросы, идеи по улучшению функционала – '
                       'пиши автору @dontbesoseriouspls ✅',

    'notready': f'К сожалению, данный раздел находится в разработке😞\n'
                f'Но ты можешь воспользовать загрузкой с <b>YouTube</b>\n'
                f'Для этого жми 👉 /youtube\n'
                f'Если есть какие-то вопросы 👉 /help',

    'help_text': f'<b>Привет!</b> С чем тебе нужна помощь?🧐\n\n'
                 f'Список доступных комманд:\n'
                 f'/youtube - Скачивание медиа с YouTube\n'
                 f'/vk - Скачивание медиа с VK\n'
                 f'/tiktok - Скачивание медиа с TikTok\n\n'
                 f'Идеи, предложения, жалобы – @dontbesoseriouspls',

    'limitation_text': 'К сожалению, запрашиваемое медиа больше 50МБ🥺\n'
                       'Так как, бот находится в разработке, действует ограничение!\n'
                       '<b>Не отчаивайтесь!</b> Скоро все заработает в полную силу😇',

    'age_error': '<b>Ой-ой!</b>\n'
                 'Кажется, на данном видео стоит возрастное ограничение🫤\n'
                 'Такие видео я еще не умею скачивать😞'
}
