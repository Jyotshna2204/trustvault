import hashlib
import json
from datetime import datetime, timezone

from flask_login import current_user
from sqlalchemy import text

from .extensions import db
from .models import AuditLog

GENESIS_HASH = "0" * 64


def _compute_hash(prev_hash, ts, actor_id, actor_email, action, outcome,
                  target_type, target_id, details):
    payload = json.dumps(
        [prev_hash, ts, actor_id, actor_email, action, outcome,
         target_type, target_id, details],
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def log_event(action, outcome="success", target_type=None, target_id=None,
              details="", actor=None, actor_email=None):
    """Append one entry to the audit log and commit it right away.

    Committing immediately means refused attempts are still recorded
    even if the request then aborts with 403/404.
    NOTE: this also commits anything else pending in the session, so call it
    AFTER the main database change has been made.
    """
    if actor is None and current_user and current_user.is_authenticated:
        actor = current_user
    actor_id = actor.id if actor else None
    if actor is not None and actor_email is None:
        actor_email = actor.email

    last = AuditLog.query.order_by(AuditLog.id.desc()).first()
    prev_hash = last.entry_hash if last else GENESIS_HASH

    ts = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    actor_email = actor_email[:255] if actor_email else None
    details = (details or "")[:1000]

    entry_hash = _compute_hash(prev_hash, ts, actor_id, actor_email, action,
                               outcome, target_type, target_id, details)
    db.session.add(AuditLog(
        timestamp=ts, actor_id=actor_id, actor_email=actor_email,
        action=action, outcome=outcome, target_type=target_type,
        target_id=target_id, details=details,
        prev_hash=prev_hash, entry_hash=entry_hash,
    ))
    db.session.commit()


def verify_chain():
    """Recompute every hash. Returns (True, None) or (False, id_of_first_bad_row)."""
    prev = GENESIS_HASH
    for row in AuditLog.query.order_by(AuditLog.id).all():
        expected = _compute_hash(prev, row.timestamp, row.actor_id,
                                 row.actor_email, row.action, row.outcome,
                                 row.target_type, row.target_id, row.details)
        if row.prev_hash != prev or row.entry_hash != expected:
            return False, row.id
        prev = row.entry_hash
    return True, None


def install_triggers():
    """Make the database itself refuse UPDATE and DELETE on audit_log."""
    db.session.execute(text(
        "CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_log "
        "BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;"))
    db.session.execute(text(
        "CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_log "
        "BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;"))
    db.session.commit()