from datetime import datetime, timezone

from flask_login import current_user
from sqlalchemy import text

from .extensions import db
from .models import AuditLog


def log_event(action, outcome="success", target_type=None, target_id=None,
              details="", actor=None, actor_email=None):
    """Add one row to the audit log. Rows are never changed or deleted."""
    if actor is None and current_user and current_user.is_authenticated:
        actor = current_user
    if actor is not None and actor_email is None:
        actor_email = actor.email
    db.session.add(AuditLog(
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        actor_id=actor.id if actor else None,
        actor_email=actor_email,
        action=action,
        outcome=outcome,
        target_type=target_type,
        target_id=target_id,
        details=(details or "")[:1000],
    ))
    db.session.commit()


def install_triggers():
    """Make the database itself refuse UPDATE and DELETE on audit_log."""
    db.session.execute(text(
        "CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_log "
        "BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;"))
    db.session.execute(text(
        "CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_log "
        "BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;"))
    db.session.commit()