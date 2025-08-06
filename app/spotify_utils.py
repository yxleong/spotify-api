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
            url = track['external_urls']['spotify']
            # track_list.append(f"{name} by {artists} check {url}")
            track_list.append({'name': name, 'artists': artists, 'url': url})


    return track_list


def classify_tracks(sp, track_ids: list, track_names: list):
    def chunks(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]

    classified = []
    for id_chunk, name_chunk in zip(chunks(track_ids, 100), chunks(track_names, 100)):
        features = sp.audio_features(id_chunk)

        for i, f in enumerate(features):
            if not f:
                continue  # skip missing data
            mood = 'Happy' if f['valence'] > 0.6 else 'Sad' if f['valence'] < 0.4 else 'Neutral'
            tempo = 'Fast' if f['tempo'] > 120 else 'Slow'

            classified.append({
                'name': name_chunk[i],
                'mood': mood,
                'tempo': tempo,
                'valence': f['valence'],
                'tempo_value': f['tempo']
            })

    return classified