import re
import shutil
import os.path

import mutagen
import mutagen.id3
import mutagen.mp3
from fuzzywuzzy import process
from mutagen.easyid3 import EasyID3

import prompt
from models import Artist, IntegrityError, Album, Genre, Song


def get_id3s_keys():
    return EasyID3.valid_keys.keys()


def get_id3(song_path):
    try:
        file = EasyID3(song_path)
    except mutagen.id3.ID3NoHeaderError:
        try:
            file = mutagen.File(song_path, easy=True)
            file.add_tags()
        except mutagen.mp3.HeaderNotFoundError as e:
            print("Song {} can't be added because: {}".format(song_path, e))
            return None
    return file


def normalize_artists():
    artists = [a.name for a in list(Artist.select().where(Artist.normalized == False))]
    for artist_name in artists:
        try:
            artist = Artist.select().where(Artist.name == artist_name).get()
        except Artist.DoesNotExist as e:
            continue
        print("Artist '{}'".format(artist_name))
        similars = [a for a in process.extract(artist_name, [a.name for a in Artist.select()], limit=50) if
                    a[1] > 90 and a[0] != artist_name]
        print("Debug similar artists with score: {} == > {}".format(
            75,
            [a for a in process.extract(artist_name, [a.name for a in Artist.select()], limit=50) if
             a[1] > 75 and a[0] != artist_name]))
        if len(similars) == 0 or not prompt.confirm("[{}] to one of {}".format(artist_name, [a[0] for a in similars])):
            artist.normalized = True
            artist.save()
            continue
        to_transform = []
        for same in similars:
            if prompt.confirm("Are they the same '{}' == '{}'".format(artist_name, same[0])):
                to_transform.append(same[0])
        for a in to_transform:
            delete_artist = Artist.select().where(Artist.name == a).get()
            delete_artist.delete_instance()
        if prompt.confirm("Change artist '{}' to an other".format(artist_name)):
            new_artist = prompt.ask("Type artist name: ", choices=to_transform)
            while not prompt.confirm("Are you sure you want to replace '{}' by '{}'".format(artist_name, new_artist)):
                new_artist = prompt.ask("Type artist name: ")
            change = Artist.select().where(Artist.name == artist_name).get()
            change.name = new_artist
            try:
                change.save()
            except IntegrityError:
                change.delete_instance()
        artist.normalized = True
        artist.save()


def populate_song(song_path, fields):
    f = get_id3(song_path)
    print(fields)
    for field in fields.keys():
        f[field] = fields[field]
    f.save()


def ask_for_fields(previous_fields):
    for k, v in previous_fields.items():
        if len(v) > 0:
            previous_fields[k] = prompt.ask_with_default(f"{k.capitalize()}", v[0], v)
        else:
            previous_fields[k] = prompt.ask_with_default(f"{k.capitalize()}", "")
    return previous_fields


def get_choices(song_infos):
    f = get_id3(song_infos["path"])
    choices = {
        "album": [song_infos.get("album"), f.get("album")] + [a.name for a in Album.select()],
        "artist": [song_infos.get("artist"), f.get("artist")] + [a.name for a in Artist.select()],
        "title": [song_infos.get("title"), f.get("title")],
        "tracknumber": [song_infos.get("tracknumber", f.get("tracknumber"))],
        "genre": [song_infos.get("genre", f.get("genre"))] + [a.name for a in Genre.select()]
    }
    new_fields = {}
    for k, v in choices.items():
        choices = [i for i in v if i]
        new_fields[k] = choices
    return new_fields


def infer_from_music_title(song_title):
    song_title = re.sub(r".mp3$", "", song_title)
    print(f"Debug with [{song_title}] !")
    regexes = [
        r"^(?P<artist>.+)\s-\s(?P<title>.+)(\.mp3)?$",
        # Put in last, this is the fall back if none is present
        r"^(?P<title>.+)(\.mp3)?$"
    ]
    for r in regexes:
        found = re.match(r, song_title)
        if found: return found.groupdict()


def save_song_to_db(song_path):
    f = get_id3(song_path)
    # genre = "ADD GENRE BITCH"
    params = {"artist": f["artist"][0], "title": f["title"][0], "location": song_path}
    params["artist"] = Artist.by_name(params["artist"]) if Artist.by_name(params["artist"]) else Artist.create(name=f"{params['artist']}", normalized=True)
    res = Song.create(**params)
    if res:
        print("Saved into DB !")


def change_downloaded_filename(song_path, base_path=""):
    f = get_id3(song_path)
    return shutil.move(song_path,
                os.path.join(base_path, "{} - {}.mp3".format(f["artist"][0], f["title"][0])))