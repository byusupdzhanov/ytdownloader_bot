import telebot
from pytube import YouTube
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

TELEGRAM_TOKEN = "6332190608:AAEJe8I3d8CW2oCxPQeFSLFoPuPcmhOl7ZE"
YOUTUBE_API_KEY = "AIzaSyAaeSLKD5o_2KQ7B_p_GsQzIiTnYHHL6Jo"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def extract_id_from_url(video_url):
    parsed_url = urlparse(video_url)
    if parsed_url.netloc == "youtu.be":
        video_id = parsed_url.path[1:]
    else:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [""])[0]
    return video_id

def get_video_title(video_url):
    try:
        video = YouTube(video_url)
        return video.title
    except Exception as e:
        print(f"Error: {e}")
        return None

def search_similar_playlists(video_title, num_playlists, page_token=None):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(
            q=video_title,
            type="playlist",
            part="id,snippet",
            maxResults=num_playlists,
            pageToken=page_token
        ).execute()

        next_page_token = search_response.get("nextPageToken", None)
        playlists = []
        for item in search_response.get("items", []):
            playlist_id = item["id"]["playlistId"]
            playlist_title = item["snippet"]["title"]
            playlists.append({"playlist_id": playlist_id, "playlist_title": playlist_title})

        return playlists, next_page_token

    except Exception as e:
        print(f"Error: {e}")
        return [], None

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Привет! Я бот для поиска похожих плейлистов на YouTube. Введите ссылку на видео или плейлист:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text

    video_id = extract_id_from_url(query)
    if video_id:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_title = get_video_title(video_url)
        if video_title:
            bot.send_message(message.chat.id, f"Похожие плейлисты для видео '{video_title}':")
            search_and_display_playlists(message.chat.id, video_title)
        else:
            bot.send_message(message.chat.id, "Не удалось получить информацию о видео.")
    else:
        # Assume it's a text query
        bot.send_message(message.chat.id, "Похожие плейлисты для запроса:")
        search_and_display_playlists(message.chat.id, query)

def search_and_display_playlists(chat_id, query):
    num_playlists = 5
    playlists, _ = search_similar_playlists(query, num_playlists)
    if not playlists:
        bot.send_message(chat_id, "По данному запросу ничего не найдено.")
        return

    response = ""
    for idx, playlist in enumerate(playlists, start=1):
        playlist_title = playlist["playlist_title"]
        playlist_id = playlist["playlist_id"]
        playlist_link = f"https://www.youtube.com/playlist?list={playlist_id}"
        response += f"{idx}. {playlist_title}\n{playlist_link}\n\n"

    bot.send_message(chat_id, response)

if __name__ == "__main__":
    bot.polling(none_stop=True)
