import os
import shutil

import music
import download
from models import Artist


class MusicDB(object):
    directories = ["/media/oddnaughty/Datas/Music"]
    youtube_dl_directory = "/media/oddnaughty/Datas/Music/ytdl"

    @classmethod
    def get_songs(cls):
        for directory in cls.directories:
            # for directory in [cls.directories[0]]:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    if filename.lower().endswith('.mp3'):
                        file_path = os.path.join(root, filename)
                        yield file_path

    @classmethod
    def fill_artist_table(cls):
        artists = cls.get_unique_by("artist")
        artists_models = []
        for artist in artists:
            artists_models.append(Artist.create_or_get(name=artist))
        return artists, artists_models

    @classmethod
    def get_unique_by(cls, key, songs=None):
        songs = songs if songs else [non_empty_song[1] for non_empty_song in
                                     [music.get_id3(s) for s in cls.get_songs()] if non_empty_song]
        to_uniques = [i[key][0] for i in songs if i.get(key, None)]
        return list(set(to_uniques))

    @classmethod
    def add_song_from_url(cls, url):
        song = download.download_song(url, cls.youtube_dl_directory)
        # TERMCOLOR FOR LOGGING IS NEEDED. AND SO DOES LOG ! :D.
        song_infos = {**song, **music.infer_from_music_title(song['title'])}
        choices = music.get_choices(song_infos)
        id3_fields = music.ask_for_fields(choices)
        music.populate_song(song['path'], id3_fields)
        new_path = music.change_downloaded_filename(song['path'], cls.youtube_dl_directory)
        music.save_song_to_db(new_path)

    @classmethod
    def move_to_ytdl(cls, filename, ytdl_path=None):
        if not ytdl_path:
            ytdl_path = cls.youtube_dl_directory
        return shutil.move(filename, os.path.join(ytdl_path, filename))