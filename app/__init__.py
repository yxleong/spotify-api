from flask import Flask, session, redirect, url_for
from flask_session import Session
from .auth import setup_spotify_oauth
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    # SESSION_TIMEOUT = timedelta(minutes=1)
    SESSION_TIMEOUT = timedelta(seconds=10)

    @app.before_request
    def session_timeout():
        now = datetime.utcnow()
        last_active_str = session.get('last_active')

        if last_active_str:
            last_active = datetime.fromisoformat(last_active_str)
            elapsed = (now - last_active).total_seconds()

            # Debug print elapsed seconds every time user makes a request
            print(f"Session active for {elapsed:.1f} seconds")

            if elapsed > SESSION_TIMEOUT.total_seconds():
                session.clear()
                # Pass a flash message or query param to show logout notice
                return redirect(url_for('main.home', timeout=1))

        session['last_active'] = now.isoformat()

    Session(app)  # Tokens hidden from client, large session data supported, safer and scalable
    setup_spotify_oauth(app)

    from .routes import main
    app.register_blueprint(main)

    return app
