import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()  # reads the .env file into environment variables


def create_app(test_config=None):
    app = Flask(__name__)

    secret = os.environ.get("SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "SECRET_KEY is not set. Copy .env.example to .env and set a value."
        )

    app.config["SECRET_KEY"] = secret
    app.config["SESSION_COOKIE_HTTPONLY"] = True   # JavaScript cannot read the cookie
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # helps against forged requests

    if test_config:
        app.config.update(test_config)  # lets our tests change settings later

    from .routes import main
    app.register_blueprint(main)

    return app