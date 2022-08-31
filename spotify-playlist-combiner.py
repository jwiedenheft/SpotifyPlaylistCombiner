#!/usr/bin/env python3
import datetime
import json
from datetime import date
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifySong:
    def __init__(self, name, artists, uri,date):
        self.name = name
        self.artists = artists
        self.uri = uri
        self.date = date
    
    
    def compare(self):
        return [self.name, self.artists]

    def to_string(self):
        return f"{self.name} by {self.artists}, released on {self.date}"

secrets_file = open('secrets.json')
secrets = json.load(secrets_file)

scope = "playlist-read-private playlist-modify-private playlist-modify-public"
spotify_auth = SpotifyOAuth(scope=scope,redirect_uri='https://github.com/jwiedenheft',client_id=secrets['client_id'],client_secret=secrets['client_secret'])

sp = spotipy.Spotify(auth_manager=spotify_auth)


def get_songs_from_playlist(playlist_in,offset=0):
    songs_out = []
    playlist_tracks = sp.playlist_items(playlist_in,offset=offset)
    if offset == 0:
        print(f"  Getting songs from {sp.playlist(playlist_in)['name']}...")
    for item in playlist_tracks['items']:
        track = item['track']
        if track == None: continue
        track_artists = []
        for artist in track['artists']:
            track_artists.append(artist['name'])
        track_date = track['album']['release_date']
        try:
            track_date = date.fromisoformat(track_date)
        except:
            # Fixes a weird edge case where a date field is assigned as just a year
            track_date = date.fromisoformat("2022-01-01")
        song = SpotifySong(track['name'],track_artists,track['uri'],track_date)
        if song not in songs_out:
            songs_out.append(song)
    if playlist_tracks['next']:
        print("    Fetching next page of tracks")
        songs_out += get_songs_from_playlist(playlist_in,offset+100)
    return songs_out


def get_songs_from_playlists(playlists_in):
    songs_out = []
    for playlist in playlists_in:
        playlist_songs = get_songs_from_playlist(playlist)
        songs_out += playlist_songs
    return songs_out



def try_add(list, track, track_dt):
    j = 0
    for i in list:
        i_track_date = i[1]
        if i_track_date > track_dt:
            list.insert(j, (track['uri'], track_dt))
            return
        j = j + 1
    list.append((track['uri'], track_dt))


def detuple(list_in):
    list_out = []
    for item in list_in:
        list_out.append(item[0])
    return list_out


def print_dates(list_in):
    for i in list_in:
        date_out = i['track']['album']['release_date']
        print(date_out)


def load_data():
    print("Loading data...")
    file_name = 'data.json'
    # if len(sys.argv) > 0:
    #    file_name = sys.argv[0]
    data_file = open(file_name)
    return json.load(data_file)


def main():
    # Load data from json file
    data = load_data()

    input_playlists = data["playlistsIn"]
    playlist_out = data["playlistOut"]
    blacklist = data["blacklist"]

    old_songs = get_songs_from_playlist(playlist_out)
    old_songs_compare = [song.compare() for song in old_songs]
    
    print("Beginning initial playlist concatenation.")
    songs_in = get_songs_from_playlists(input_playlists)
    print("Completed initial playlist concatenation.")

    print("Filtering for 2022 songs.")
    songs_2022 = [song for song in songs_in if song.date.year == 2022] 

    print("Beginning blacklist removal.")
    blacklist_songs = get_songs_from_playlist(blacklist)
    blacklist_compare = [song.compare() for song in blacklist_songs]
    songs_no_blacklist = [song for song in songs_2022 if song.compare() not in blacklist_compare]
    print("Blacklist removal complete.")

    print ("Checking for songs not already on playlist...")
    songs_to_add = []
    for song in songs_no_blacklist:
        if song.compare() not in old_songs_compare and song.uri not in songs_to_add:
            print(f"  New song: {song.name} by {str(song.artists).replace('[','').replace(']','')}")
            songs_to_add.append(song.uri)
    
    print(f"Adding {len(songs_to_add)} songs total...")
    sp.playlist_add_items(playlist_out,songs_to_add)
    print("All songs added. Enjoy your playlist!")


if __name__ == "__main__":
    main()
