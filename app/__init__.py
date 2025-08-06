from flask import Flask
from flask_session import Session
from .auth import setup_spotify_oauth

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    Session(app)  # Tokens hidden from client, large session data supported, safer and scalable
    setup_spotify_oauth(app)

    from .routes import main
    app.register_blueprint(main)

    return app
