from flask import Blueprint, render_template
from flask_login import current_user, login_required

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