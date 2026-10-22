from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager

ROLE_ADMIN = "admin"
ROLE_OWNER = "owner"
ROLE_VIEWER = "viewer"
ROLES = (ROLE_ADMIN, ROLE_OWNER, ROLE_VIEWER)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    @property
    def is_active(self):
        # Flask-Login checks this on every request. Turning a user off
        # makes their existing session stop working immediately.
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    # Runs on EVERY request: the user and role are re-read from the database,
    # never trusted from the cookie. Changes to role/active apply immediately.
    user = db.session.get(User, int(user_id))
    if user is None or not user.active:
        return None
    return user