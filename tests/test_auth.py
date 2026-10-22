from app.extensions import db
from app.models import User
from tests.conftest import login


def test_login_success_and_dashboard(client, make_user):
    email, pw = make_user("a@x.test", "viewer")
    r = login(client, email, pw)
    assert r.status_code == 302
    assert client.get("/dashboard").status_code == 200


def test_wrong_password_rejected(client, make_user):
    email, _ = make_user("a@x.test", "viewer")
    r = login(client, email, "wrong")
    assert r.status_code == 200
    assert client.get("/dashboard").status_code == 302  # still logged out


def test_unknown_email_gives_same_message(client, make_user):
    make_user("a@x.test", "viewer")
    r1 = login(client, "a@x.test", "wrong")
    r2 = login(client, "nobody@x.test", "wrong")
    assert b"Invalid email or password." in r1.data
    assert b"Invalid email or password." in r2.data


def test_anonymous_redirected_from_dashboard(client):
    assert client.get("/dashboard").status_code == 302


def test_viewer_cannot_open_admin(client, make_user):
    email, pw = make_user("v@x.test", "viewer")
    login(client, email, pw)
    assert client.get("/admin").status_code == 403


def test_owner_cannot_open_admin(client, make_user):
    email, pw = make_user("o@x.test", "owner")
    login(client, email, pw)
    assert client.get("/admin").status_code == 403


def test_admin_can_open_admin(client, make_user):
    email, pw = make_user("ad@x.test", "admin")
    login(client, email, pw)
    assert client.get("/admin").status_code == 200


def test_deactivated_user_loses_access_immediately(app, client, make_user):
    email, pw = make_user("a@x.test", "viewer")
    login(client, email, pw)
    assert client.get("/dashboard").status_code == 200
    with app.app_context():
        u = User.query.filter_by(email=email).first()
        u.active = False
        db.session.commit()
    assert client.get("/dashboard").status_code == 302  # session now useless


def test_logout_requires_post(client, make_user):
    email, pw = make_user("a@x.test", "viewer")
    login(client, email, pw)
    assert client.get("/logout").status_code == 405