from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length

from .audit import log_event
from .models import User

auth = Blueprint("auth", __name__)

_DUMMY_HASH = generate_password_hash("not-a-real-password")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=200)])


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user is None:
            check_password_hash(_DUMMY_HASH, form.password.data)
            password_ok = False
        else:
            password_ok = user.check_password(form.password.data)

        if user and password_ok and user.active:
            session.clear()
            login_user(user)
            log_event("login", "success", "user", user.id, actor=user)
            return redirect(url_for("main.dashboard"))

        # Never log the password. Log who was tried, so attacks are visible.
        log_event("login", "failure", "user", user.id if user else None,
                  details="bad credentials or inactive account",
                  actor=None, actor_email=email)
        flash("Invalid email or password.", "error")

    return render_template("login.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    log_event("logout", "success", "user", current_user.id)
    logout_user()
    session.clear()
    return redirect(url_for("main.home"))