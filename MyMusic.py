import os
import shutil
import sys
import mutagen
import mutagen.id3
from mutagen.easyid3 import EasyID3
from youtube_dl import YoutubeDL
from pprint import pprint


class MyMusic(object):
    """
    A class that can make me confortable with my music o/
    """

    def __init__(self, yt_path=os.path.join(os.environ["HOME"], "Music/ytdl")):
        """
        :param yt_path: The directory to store da shit bitch
        """
        self.old_tags = {}
        self.yt_path = yt_path
        self.genres = ["Acid", "Acidcore", "Tribe", "Mental", "Tekno", "Hardtek", "Raggatek", "Tribecore", "Hardstyle", "Hardcore", "Frenchcore", "Electro", "Melodic Techno", "Dubstep", "Drum'n'Bass", "Crossbreed", "Psytrance", "Hi-Tech", "Psytribe", "Trap", "Rock Psychedelique", "Hip-Hop", "Rap"]

    def song_to_directory(self, path, filename, album="", genres=[], tracknumber=""):
        """
        Edit the mp3 file (filename) metadatas if needed and put it in path/Artist/{Album}/Title
        """
        datas = filename.split(' - ')
        if len(datas) < 2:
            datas = filename.split('-')
        try:
            file = EasyID3(os.path.join(path, filename))
        except mutagen.id3.ID3NoHeaderError:
            file = mutagen.File(os.path.join(path, filename), easy=True)
            file.add_tags()
        print(datas)
        try:
            datas = {
                "title": file.get("title", []) or [(datas[2][:-4] if len(datas) > 2 else datas[1][:-4])],
                "artist": file.get("artist", []) or [(datas[1] if len(datas) > 2 else datas[0])],
                "tracknumber": file.get("tracknumber", []) or [tracknumber] or [(datas[0] if len(datas) > 2 else "")],
                "album": file.get("album", []) or self.old_tags['album'] if 'album' in self.old_tags else [album],
                "genre": file.get("genre", []) or self.old_tags['genre'] if 'genre' in self.old_tags else [";".join(list(map(str.capitalize, genres)))],
            }
        except IndexError as e:
            datas = {
                "title": file.get("title", []) or [(datas[2][:-4] if len(datas) > 2 else datas[0][:-4])],
                "artist": file.get("artist", []) or [(datas[1] if len(datas) > 2 else "")],
                "tracknumber": file.get("tracknumber", []) or [tracknumber] or [(datas[0] if len(datas) > 2 else "")],
                "album": file.get("album", []) or self.old_tags['album'] if 'album' in self.old_tags else [album],
                "genre": file.get("genre", []) or self.old_tags['genre'] if 'genre' in self.old_tags else [";".join(list(map(str.capitalize, genres)))],
            }
        zap = input("Informations pour {}\nZapper [z]\n{} : ".format(filename, datas))
        if zap != "z":
            datas = self.get_input_attributes(datas)
        print(datas)
        for k in datas.keys():
            file[k] = datas[k]
            self.old_tags[k] = datas[k] or self.old_tags.get(k, [])
        file.save()
        shutil.move(os.path.join(path, filename), os.path.join(path, "{} - {}.mp3".format(file["artist"][0], file["title"][0])))

    def get_input_attributes(self, datas):
        """
        Function asking the metadatas via command-line input"
        :param datas: Already filled datas dict
        :return: datas ^_^
        """
        for i in datas.keys():
            if i == "genre":
                datas[i] = self.manage_genre()
            else:
                r = input('Please enter {}[{}/{}][type 1 to chose the second] : '.format(i, datas[i], self.old_tags.get(i, "")))
                if r:
                    if r == "1":
                        datas[i] = self.old_tags.get(i, "")
                    else:
                        datas[i] = [r]
        return datas

    def manage_genre(self):
            new = []
            print("Choose genre(s). If multiple, do ';' between choices. Type 'a' to add a new genre")
            for i, v in enumerate(self.genres):
                print("{} - {}".format(i, v))
            r = input("Choice(s): ").split(';')
            if r == ["a"]:
                self.genres.append(input("New genre: ").strip())
                return (self.manage_genre())
            else:
                try:
                    new = [";".join(map(lambda l: self.genres[int(l)], r))]
                except ValueError as e:
                    print("Please enter a number...")
                    return self.manage_genre()
                return new

    def get_song_from_yt(self, url, playlist=False):
        """
        Download a song from youtube or soundcloud and put it in self.yt_path converted to mp3 with filled metadatas
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'nocheckcertificate': False,
            'noplaylist': not playlist,
            'outtmpl': os.path.join(self.yt_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            datas = ydl.extract_info(url)
            if playlist:
                for i, song in enumerate(datas['entries']):
                    self.song_to_directory(self.yt_path, song['title'] + ".mp3", album=datas['title'], tracknumber=str(i + 1))
            else:
                self.song_to_directory(self.yt_path, datas['title'] + ".mp3")
            return True

    def sort_directory(self, dir_path):
        """
        Given a dir_path directory, self.song_to_directory every file from this directory
        """
        for file in sorted([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]):
            self.song_to_directory(dir_path, file)
