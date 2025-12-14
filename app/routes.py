from flask import Blueprint, redirect, request, session, url_for, render_template_string
from spotipy import Spotify
import pandas as pd
from .auth import sp_oauth
from .spotify_utils import get_all_playlist_tracks

main = Blueprint('main', __name__)
main.register_blueprint(reccobeats_bp)

@main.route('/')
def home():
    token_info = sp_oauth.cache_handler.get_cached_token()
    if not sp_oauth.validate_token(token_info):
        return redirect(sp_oauth.get_authorize_url())
    
    auth_url = sp_oauth.get_authorize_url()
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
    
    playlists_info = [(pl['name'], pl['id']) for pl in playlists['items']]
    playlist_html = '<h2>Your Playlists</h2><ul>'
    for name, pid in playlists_info:
        playlist_html += f'<li>{name} - <a href="/playlist/{pid}">View tracks</a></li>'
    playlist_html += '</ul>'
    playlist_html += f"<p><a href='/logout'>Logout</a></p>"

    return playlist_html


@main.route('/playlist/<playlist_id>')
def show_playlist_tracks(playlist_id):
    token_info = sp_oauth.cache_handler.get_cached_token()
    if not sp_oauth.validate_token(token_info):
        return redirect(sp_oauth.get_authorize_url())

    sp = Spotify(auth=token_info['access_token'])
    tracks = get_all_playlist_tracks(sp, playlist_id)
    
    playlist_tracks_html = f'<h2>Tracks in Playlist</h2><ul>'
    if not tracks:
        playlist_tracks_html += '<p>No tracks found in this playlist.</p></ul>'
    else:
        for i, track in enumerate(tracks):
            playlist_tracks_html += (f'<li>{track["name"]} by {track["artists"]} '
                f'- <a href="{track["url"]}" target="_blank" rel="noopener noreferrer">Listen</a>'
                f'</li>')
        playlist_tracks_html += '</ul>'
        playlist_tracks_html += f"<p><a href='/playlist/{playlist_id}/features'>Analyze</a></p>"
        
    playlist_tracks_html += f"<p><a href='/logout'>Logout</a></p>"

    return playlist_tracks_html


# @main.route('/playlist/<playlist_id>/analyze')
# def analyze_playlist(playlist_id):
#     token_info = sp_oauth.cache_handler.get_cached_token()
#     if not sp_oauth.validate_token(token_info):
#         return redirect(sp_oauth.get_authorize_url())

#     sp = Spotify(auth=token_info['access_token'])
#     tracks = get_all_playlist_tracks(sp, playlist_id)

#     analyze_html = '<h2>Playlist Track Analysis</h2>'
#     if not tracks:
#         analyze_html += '<li>No tracks found in this playlist.</li>'
#     else:
#         track_ids = [s['id'] for s in tracks if 'id' in s]
#         track_features = []      
#         batch_size = 1
#         for i in range(0, len(track_ids), batch_size):
#             batch = track_ids[i:i+batch_size]
#             features = sp.audio_features(batch)
#             features = [f for f in features if f is not None]
#             track_features.extend(features)

#         columns = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
#                 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
#                 'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms']
#         tf_df = pd.DataFrame(track_features, columns=columns)

#         artist_genres = []
#         for s in tracks:
#             artist_info = sp.artist(s['artist_ids'][0])
#             artist_genres.append(", ".join(artist_info.get('genres', [])))
#         tf_df['artist_genres'] = artist_genres

#     analyze_html += tf_df.head(10).to_html(classes='table table-striped', index=False)
#     analyze_html += "<p><a href='/logout'>Logout</a></p>"

#     return analyze_html


@main.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for('main.home'))
