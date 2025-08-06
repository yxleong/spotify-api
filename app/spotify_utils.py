from spotipy import Spotify

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
            name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            track_list.append(f"{name} by {artists}")

    return track_list
