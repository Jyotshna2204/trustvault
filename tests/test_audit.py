import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.audit import verify_chain
from app.extensions import db
from app.models import AuditLog
from tests.conftest import login


def test_login_success_and_failure_are_logged(app, client, make_user):
    email, pw = make_user("a@x.test", "viewer")
    login(client, email, "wrong")
    login(client, email, pw)
    with app.app_context():
        rows = AuditLog.query.order_by(AuditLog.id).all()
        assert [(r.action, r.outcome) for r in rows] == [
            ("login", "failure"), ("login", "success")]
        assert rows[0].actor_email == "a@x.test"


def test_password_never_written_to_log(app, client, make_user):
    email, _ = make_user("a@x.test", "viewer")
    login(client, email, "SuperSecretGuess99")
    with app.app_context():
        for r in AuditLog.query.all():
            assert "SuperSecretGuess99" not in (r.details or "")


def test_chain_verifies_when_untouched(app, client, make_user):
    email, pw = make_user("a@x.test", "viewer")
    login(client, email, "wrong")
    login(client, email, pw)
    with app.app_context():
        assert verify_chain() == (True, None)


def test_database_blocks_update_and_delete(app, client, make_user):
    email, _ = make_user("a@x.test", "viewer")
    login(client, email, "wrong")
    with app.app_context():
        with pytest.raises(DBAPIError):
            db.session.execute(text("UPDATE audit_log SET action='x'"))
        db.session.rollback()
        with pytest.raises(DBAPIError):
            db.session.execute(text("DELETE FROM audit_log"))
        db.session.rollback()


def test_tampering_is_detected_if_triggers_are_bypassed(app, client, make_user):
    email, pw = make_user("a@x.test", "viewer")
    login(client, email, "wrong")
    login(client, email, pw)
    with app.app_context():
        db.session.execute(text("DROP TRIGGER audit_no_update"))
        db.session.execute(text("UPDATE audit_log SET outcome='success' WHERE id=1"))
        db.session.commit()
        ok, bad_id = verify_chain()
        assert ok is False
        assert bad_id == 1


def test_only_admin_can_view_audit_page(client, make_user):
    email, pw = make_user("v@x.test", "viewer")
    login(client, email, pw)
    assert client.get("/admin/audit").status_code == 403
    client.post("/logout")
    email, pw = make_user("ad@x.test", "admin")
    login(client, email, pw)
    assert client.get("/admin/audit").status_code == 200