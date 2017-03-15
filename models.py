from peewee import *

DATABASE_NAME = "/home/oddnaughty/.music_library.db"
DB = SqliteDatabase(DATABASE_NAME)


class BaseModel(Model):
    class Meta:
        database = DB


class Genre(BaseModel):
    name = CharField(unique=True)


class Album(BaseModel):
    name = CharField(unique=True)


class Artist(BaseModel):
    # first_name = CharField()
    # last_name = CharField()
    name = CharField(unique=True)
    normalized = BooleanField(default=False)
    # birth_date = DateTimeField()

    @classmethod
    def by_name(cls, name):
        try:
            return Artist.select().where(Artist.name == name).get()
        except Artist.DoesNotExist as e:
            return None

    @classmethod
    def get_names(cls):
        return [a.name for a in Artist.select().where(Artist.normalized)]

    class Meta:
        order_by = ('normalized', 'name')


class Song(BaseModel):
    artist = ForeignKeyField(Artist, related_name="artist")
    # album = ForeignKeyField(Album)
    # composer = CharField()
    # genre = ManyToManyField(Genre, related_name="genres")
    # date = DateTimeField()
    # lyricist = CharField()
    title = CharField()
    location = CharField(unique=True)
    # version = CharField()
    track_number = IntegerField(null=True)

    class Meta:
        order_by = ('artist', 'title')


class SongGenres(BaseModel):
    song = ForeignKeyField(Song)
    genre = ForeignKeyField(Genre)


class AlbumArtists(BaseModel):
    artist = ForeignKeyField(Artist)
    album = ForeignKeyField(Album)


def recreate_tables():
    DB.connect()
    DB.drop_tables([Genre, Song, Artist, Album, SongGenres, AlbumArtists], safe=True)
    DB.create_tables([Genre, Song, Artist, Album, SongGenres, AlbumArtists])
