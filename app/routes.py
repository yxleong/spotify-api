from flask import Blueprint, redirect, request, session, url_for
from spotipy import Spotify
from .auth import sp_oauth

main = Blueprint('main', __name__)
sp = Spotify(auth_manager=sp_oauth)

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
    info = [f"{pl['name']}: {pl['external_urls']['spotify']}" for pl in playlists['items']]
    return '<br>'.join(info)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
