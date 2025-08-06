from flask import Blueprint, redirect, request, session, url_for, render_template_string
from spotipy import Spotify
from .auth import sp_oauth
# from .spotify_utils import get_all_playlist_tracks, classify_tracks
from .spotify_utils import get_all_playlist_tracks

main = Blueprint('main', __name__)

@main.route('/')
def home():
    token_info = sp_oauth.cache_handler.get_cached_token()
    if not sp_oauth.validate_token(token_info):
        return redirect(sp_oauth.get_authorize_url())
    auth_url = sp_oauth.get_authorize_url()
    # return redirect(url_for('.get_playlists'))
    return render_template_string("""
        <h2>Login</h2>
        <p><a href="{{ auth_url }}">Login with Spotify</a></p>
    """, auth_url=auth_url)


@main.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return render_template_string("""
            <h2>Authorization Failed</h2>
            <p>You cancelled the Spotify authorization or an error occurred: {{ error }}</p>
            <p><a href="{{ url_for('main.home') }}">Try to log in again</a></p>
        """, error=error)
    
    code = request.args.get('code')
    if not code:
        return render_template_string("""
            <h2>Authorization Error</h2>
            <p>Missing authorization code. Please try logging in again.</p>
            <p><a href="{{ url_for('main.home') }}">Login</a></p>
        """)
    
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
    playlist_html += f"<p><a href='/logout'>Logout</a></p>"

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
    html += f"<p><a href='/logout'>Logout</a></p>"

    return html


@main.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for('main.home'))
