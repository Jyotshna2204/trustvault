import os

from dotenv import load_dotenv
from flask import Flask, render_template
from .extensions import csrf, db, login_manager
from .docs import docs
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trustvault.db"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB request limit
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(app.root_path), "uploads")
    app.register_blueprint(docs)
    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Copy .env.example to .env and set a value."
        )

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"

    from . import models  # noqa: F401  (registers the tables)
    from .auth import auth
    from .routes import main
    from .docs import docs

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(docs)
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message="Forbidden"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Not found"), 404

    with app.app_context():
        db.create_all()
        from .audit import install_triggers
        install_triggers()

    return app