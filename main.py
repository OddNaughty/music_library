import argparse
from MyMusicLibrary import MusicDB


def main(url):
    """
    Requirements: youtube_dl, mutagen
    """
    MusicDB.add_song_from_url(url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to download a youtube/soundcloud video and convert to mp3")
    parser.add_argument('url')
    # parser.add_argument('-yt_path', help="The directory to store the converted files")
    # parser.add_argument('--with_playlist', help="The boolean to download a playlist", action="store_true")
    args = parser.parse_args()
    # main(args.url, args.yt_path, args.with_playlist)
    main(args.url)
