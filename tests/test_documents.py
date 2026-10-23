import io

from app.models import Document, User
from tests.conftest import login
from app.extensions import db

def make_client(app, make_user, name, role):
    email, pw = make_user(f"{name}@x.test", role)
    c = app.test_client()
    login(c, email, pw)
    return c


def upload_doc(client):
    return client.post("/documents/upload", data={
        "title": "Doc1", "category": "general",
        "file": (io.BytesIO(b"%PDF-1.4 secret"), "a.pdf")},
        content_type="multipart/form-data")


def setup(app, make_user):
    owner1 = make_client(app, make_user, "owner1", "owner")
    owner2 = make_client(app, make_user, "owner2", "owner")
    viewer = make_client(app, make_user, "viewer", "viewer")
    admin = make_client(app, make_user, "admin", "admin")
    upload_doc(owner1)
    return owner1, owner2, viewer, admin


def test_owner_can_download(app, make_user):
    owner1, *_ = setup(app, make_user)
    r = owner1.get("/documents/1/download")
    assert r.status_code == 200
    assert r.data == b"%PDF-1.4 secret"


def test_stranger_cannot_read_download_edit_delete(app, make_user):
    _, owner2, viewer, _ = setup(app, make_user)
    for c in (owner2, viewer):
        assert c.get("/documents/1").status_code == 403
        assert c.get("/documents/1/download").status_code == 403
        assert c.post("/documents/1/edit", data={"title": "hacked"}).status_code == 403
        assert c.post("/documents/1/delete").status_code == 403
        assert c.post("/documents/1/grant", data={"email": "viewer@x.test", "level": "edit"}).status_code == 403
    with app.app_context():
        assert db.session.get(Document, 1).title == "Doc1"


def test_read_grant_allows_download_but_not_edit(app, make_user):
    owner1, _, viewer, _ = setup(app, make_user)
    owner1.post("/documents/1/grant", data={"email": "viewer@x.test", "level": "read"})
    assert viewer.get("/documents/1/download").status_code == 200
    assert viewer.post("/documents/1/edit", data={"title": "x"}).status_code == 403


def test_revoke_works_immediately(app, make_user):
    owner1, _, viewer, _ = setup(app, make_user)
    owner1.post("/documents/1/grant", data={"email": "viewer@x.test", "level": "read"})
    assert viewer.get("/documents/1/download").status_code == 200
    with app.app_context():
        uid = User.query.filter_by(email="viewer@x.test").first().id
    owner1.post(f"/documents/1/revoke/{uid}")
    assert viewer.get("/documents/1/download").status_code == 403


def test_admin_cannot_read_but_can_delete(app, make_user):
    owner1, _, _, admin = setup(app, make_user)
    assert admin.get("/documents/1/download").status_code == 403
    assert admin.post("/documents/1/delete").status_code == 302
    assert owner1.get("/documents/1/download").status_code == 403  # gone


def test_bad_file_type_rejected(app, make_user):
    owner1, *_ = setup(app, make_user)
    owner1.post("/documents/upload", data={
        "title": "Bad", "category": "general",
        "file": (io.BytesIO(b"MZ"), "evil.exe")},
        content_type="multipart/form-data")
    with app.app_context():
        assert Document.query.filter_by(title="Bad").count() == 0


def test_viewer_cannot_upload(app, make_user):
    _, _, viewer, _ = setup(app, make_user)
    assert viewer.get("/documents/upload").status_code == 403


def test_denied_attempt_is_logged(app, make_user):
    from app.models import AuditLog
    _, owner2, _, _ = setup(app, make_user)
    owner2.get("/documents/1/download")
    with app.app_context():
        assert AuditLog.query.filter_by(action="read", outcome="denied").count() == 1
def test_search_never_shows_other_peoples_documents(app, make_user):
    owner1, owner2, _, _ = setup(app, make_user)
    assert b"Doc1" in owner1.get("/documents/?title=Doc").data
    assert b"Doc1" not in owner2.get("/documents/?title=Doc").data