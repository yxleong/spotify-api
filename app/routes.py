from flask import Blueprint, redirect, request, session, url_for
from spotipy import Spotify
from .auth import sp_oauth
# from .spotify_utils import get_all_playlist_tracks, classify_tracks
from .spotify_utils import get_all_playlist_tracks

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if not sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token()):
        return redirect(sp_oauth.get_authorize_url())
    return redirect(url_for('.get_playlists'))

@main.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('.get_playlists'))

@main.route('/get_playlists')
def get_playlists():
    token_info = sp_oauth.cache_handler.get_cached_token()
    if not sp_oauth.validate_token(token_info):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    sp = Spotify(auth=token_info['access_token'])
    playlists = sp.current_user_playlists()
    # info = [f"{pl['name']}: {pl['external_urls']['spotify']}" for pl in playlists['items']]
    # return '<br>'.join(info)
    
    playlists_info = [(pl['name'], pl['id']) for pl in playlists['items']]
    playlist_html = '<h2>Your Playlists</h2><ul>'
    for name, pid in playlists_info:
        playlist_html += f'<li>{name} - <a href="/playlist/{pid}">View Songs</a></li>'
    playlist_html += '</ul>'

    return playlist_html


@main.route('/playlist/<playlist_id>')
def show_playlist_songs(playlist_id):
    token_info = sp_oauth.cache_handler.get_cached_token()
    if not sp_oauth.validate_token(token_info):
        return redirect(sp_oauth.get_authorize_url())

    sp = Spotify(auth=token_info['access_token'])
    songs = get_all_playlist_tracks(sp, playlist_id)

    track_ids = [song['url'].split('/')[-1] for song in songs]
    track_names = [song['name'] for song in songs]
    
    # classified_tracks = classify_tracks(sp, track_ids, track_names)
    
    html = f'<h2>Songs in Playlist</h2><ul>'
    if not songs:
        html += '<li>No songs found in this playlist.</li>'
    else:
        for i, song in enumerate(songs):
            classification = ''
            # if i < len(classified_tracks):
            #     c = classified_tracks[i]
            #     classification = f" - Mood: {c['mood']}, Tempo: {c['tempo']}"
            html += (f'<li>{song["name"]} by {song["artists"]} '
                     f'- <a href="{song["url"]}" target="_blank" rel="noopener noreferrer">Listen</a>'
                     f'{classification}</li>')
    html += '</ul>'

    return html


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
