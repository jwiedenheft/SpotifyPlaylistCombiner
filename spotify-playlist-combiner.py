#!/usr/bin/env python3

import json
from datetime import date
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-read-private playlist-modify-private playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


def get_songs_from_playlists(playlists_in):
    songs_in = []
    for pl in playlists_in:
        playlist = sp.playlist(pl)
        print(f"    Getting songs from {playlist['name']}...")
        for item in playlist['tracks']['items']:
            track = item['track']
            if track == None: continue
            track_date = date.fromisoformat(track['album']['release_date'])
            if track_date.year == 2022 and ((track['uri'], track_date) not in songs_in):
                try_add(songs_in, track, track_date)
    return detuple(songs_in)


def try_add(ls, track, track_dt):
    j = 0
    for i in ls:
        i_track_date = i[1]
        if i_track_date > track_dt:
            ls.insert(j, (track['uri'], track_dt))
            return
        j = j + 1
    ls.append((track['uri'], track_dt))


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

    print("Beginning initial playlist concatenation.")
    songs = get_songs_from_playlists(input_playlists)
    print("Completed initial playlist concatenation.")
    print("Beginning blacklist removal.")
    blacklist_songs = get_songs_from_playlists(blacklist)
    songs_to_add = [song for song in songs if song not in blacklist_songs]
    print("Blacklist removal complete.")

    print("Beginning clearing output playlist.")
    old_songs = get_songs_from_playlists({playlist_out})
    sp.playlist_remove_all_occurrences_of_items(playlist_out, old_songs)
    print("Completed clearing output playlist.")

    print(f"Adding {len(songs_to_add)} songs...")
    while len(songs_to_add) > 100:
        first_100_songs = songs_to_add[0:99]
        rest_of_songs = songs_to_add[100:len(songs_to_add)]
        sp.playlist_add_items(playlist_out, first_100_songs)
        songs_to_add = rest_of_songs
    sp.playlist_add_items(playlist_out, songs_to_add)
    print("All songs added. Enjoy your playlist!")


if __name__ == "__main__":
    main()
