import os

from youtube_dl import YoutubeDL


def ytdl_opts(playlist, base_path):
    ytdl_opts = {
        'format': 'bestaudio/best',
        'nocheckcertificate': False,
        'noplaylist': not playlist,
        'outtmpl': os.path.join(base_path, '%(title)s.%(ext)s'),
        'embedthumbnail': True,
        'writethumbnail': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    }
    return ytdl_opts


def download_playlist(url, base_path=""):
    with YoutubeDL(ytdl_opts(True, base_path)) as ydl:
        data = ydl.extract_info(url)
        ret = []
        for i, song in enumerate(data['entries']):
            ret.append({
                'title': song['title'] + ".mp3",
                'album': data['title'],
                'tracknumber': str(i + 1),
                'path': os.path.join(base_path, data['title'] + ".mp3")
            })
        return ret


def download_song(url, base_path=""):
    with YoutubeDL(ytdl_opts(False, base_path)) as ydl:
        data = ydl.extract_info(url)
        if data["thumbnails"] and "filename" in data["thumbnails"][0].keys():
            os.remove(os.path.join(base_path, data["thumbnails"][0]["filename"]))
        return {
            'title': data['title'] + ".mp3",
            'path': os.path.join(base_path, data['title'] + ".mp3")
        }
