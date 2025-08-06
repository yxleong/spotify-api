import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env file

class Config:
    SECRET_KEY = os.urandom(64)
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = "http://127.0.0.1:5000/callback"
    SCOPE = "playlist-read-private"
