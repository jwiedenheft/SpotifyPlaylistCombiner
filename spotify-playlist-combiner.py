import sys
import json
from datetime import date
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-read-private playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


def get_songs_from_playlists(playlists_in):
    songs_in = []
    for pl in playlists_in:
        playlist = sp.playlist(pl)
        for item in playlist['tracks']['items']:
            track = item['track']
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
    file_name = "data.json"
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

    songs = get_songs_from_playlists(input_playlists)

    sp.playlist_remove_all_occurrences_of_items(playlist_out, songs)
    sp.playlist_add_items(playlist_out, songs)

    # Remove blacklisted songs
    sp.playlist_remove_all_occurrences_of_items(playlist_out, get_songs_from_playlists(blacklist))

    playlist_songs = sp.playlist(playlist_out)['tracks']['items']

    # For Debug:
    # print_dates(playlist_songs)

if __name__ == "__main__":
    main()