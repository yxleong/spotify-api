from spotipy import Spotify
import pandas as pd

def get_all_playlist_tracks(sp: Spotify, playlist_id: str):
    tracks = []
    results = sp.playlist_tracks(playlist_id, limit=100)
    tracks.extend(results['items'])

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    track_list = []
    for item in tracks:
        track = item['track']
        if track:
            id = track['id']
            name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            url = track['external_urls']['spotify']
            track_list.append({'id': id, 'name': name, 'artists': artists, 'url': url})

    return track_list