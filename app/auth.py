from flask import session
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

sp_oauth = None

def setup_spotify_oauth(app):
    global sp_oauth
    sp_oauth = SpotifyOAuth(
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
        redirect_uri=app.config['REDIRECT_URI'],
        scope=app.config['SCOPE'],
        cache_handler=FlaskSessionCacheHandler(session),
        show_dialog = True
    )
