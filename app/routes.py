from flask import Blueprint, render_template
from flask_login import current_user, login_required
from .audit import verify_chain
from .models import AuditLog
from .decorators import role_required
from .models import ROLE_ADMIN, User

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@main.route("/admin")
@role_required(ROLE_ADMIN)
def admin():
    users = User.query.order_by(User.id).all()
    return render_template("admin.html", users=users)
@main.route("/admin/audit")
@role_required(ROLE_ADMIN)
def admin_audit():
    ok, bad_id = verify_chain()
    entries = AuditLog.query.order_by(AuditLog.id.desc()).limit(200).all()
    return render_template("audit.html", entries=entries, ok=ok, bad_id=bad_id)