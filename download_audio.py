from youtube_dl import YoutubeDL
from pprint import pprint


def download_audio(link):
    audio_downloader = YoutubeDL({'format': 'bestaudio', 'default_search': 'auto'})
    try:
        URL = link
        if 'list' in URL:
            return False, 'Я пока не умею работать с плейлистами'
        elif '/' in URL:
            info = audio_downloader.extract_info(URL, download=False)
            uploader = info['uploader']
            uploader_url = info['uploader_url']
            url = info['webpage_url']
            file = info['formats'][0]['url']
            title = info["title"]
            duration = info["duration"]
            thumbnail = info["thumbnail"]
        else:
            info = audio_downloader.extract_info(URL, download=False)
            uploader = info['entries'][0]['uploader']
            uploader_url = info['entries'][0]['uploader_url']
            url = info['entries'][0]['webpage_url']
            file = info['entries'][0]['formats'][0]['url']
            title = info['entries'][0]["title"]
            duration = info['entries'][0]["duration"]
            thumbnail = info['entries'][0]["thumbnail"]
        return True, file, title, duration, uploader, uploader_url, url, thumbnail

    except Exception:
        return False, "Какая-то ошибка при воспроизведении", None, None, None, None, None, None