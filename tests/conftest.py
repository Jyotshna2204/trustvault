import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    def _make(email, role, password="pw-12345"):
        with app.app_context():
            u = User(email=email, name=email.split("@")[0], role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
        return email, password
    return _make


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password})
@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "UPLOAD_FOLDER": str(tmp_path),
    })