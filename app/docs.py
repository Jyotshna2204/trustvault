import os
import secrets

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for)
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from .audit import log_event
from .decorators import role_required
from .extensions import db
from .models import Document, Grant, User
from .permissions import can

docs = Blueprint("docs", __name__, url_prefix="/documents")

ALLOWED = {"pdf", "txt", "png", "jpg", "jpeg", "docx"}
MAX_BYTES = 4 * 1024 * 1024


def get_doc(doc_id, action):
    """Load a document only if the user may do `action`. Otherwise log and 403."""
    doc = db.session.get(Document, doc_id)
    if doc is None or not can(current_user, doc, action):
        log_event(action, "denied", "document", doc_id)
        abort(403)
    return doc


@docs.route("/")
@login_required
def index():
    shared = db.session.query(Grant.document_id).filter_by(user_id=current_user.id)
    items = Document.query.filter(
        or_(Document.owner_id == current_user.id, Document.id.in_(shared))
    ).all()
    return render_template("documents.html", docs=items)


@docs.route("/upload", methods=["GET", "POST"])
@role_required("owner")
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "general").strip()
        name = secure_filename(f.filename) if f else ""
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        data = f.read(MAX_BYTES + 1) if f else b""

        if not title or not name:
            flash("Title and file are required.", "error")
        elif ext not in ALLOWED:
            flash("File type not allowed.", "error")
        elif len(data) == 0 or len(data) > MAX_BYTES:
            flash("File must not be empty and must be under 4 MB.", "error")
        else:
            stored = secrets.token_hex(16)  # random name, not the user's
            with open(os.path.join(current_app.config["UPLOAD_FOLDER"], stored), "wb") as out:
                out.write(data)
            doc = Document(title=title, category=category, owner_id=current_user.id,
                           original_filename=name, stored_name=stored)
            db.session.add(doc)
            db.session.commit()
            log_event("upload", "success", "document", doc.id, details=name)
            return redirect(url_for("docs.detail", doc_id=doc.id))
        log_event("upload", "failure", "document", None, details=name)
    return render_template("upload.html")


@docs.route("/<int:doc_id>")
@login_required
def detail(doc_id):
    doc = get_doc(doc_id, "read")
    grants = Grant.query.filter_by(document_id=doc.id).all()
    return render_template("document.html", doc=doc, grants=grants,
                           is_owner=doc.owner_id == current_user.id,
                           can_edit=can(current_user, doc, "edit"))


@docs.route("/<int:doc_id>/download")
@login_required
def download(doc_id):
    doc = get_doc(doc_id, "read")          # <-- the download decision
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], doc.stored_name)
    log_event("download", "success", "document", doc.id)
    return send_file(path, as_attachment=True, download_name=doc.original_filename)


@docs.route("/<int:doc_id>/edit", methods=["POST"])
@login_required
def edit(doc_id):
    doc = get_doc(doc_id, "edit")
    title = request.form.get("title", "").strip()
    if title:
        doc.title = title
        db.session.commit()
        log_event("update", "success", "document", doc.id)
    return redirect(url_for("docs.detail", doc_id=doc.id))


@docs.route("/<int:doc_id>/delete", methods=["POST"])
@login_required
def delete(doc_id):
    doc = get_doc(doc_id, "delete")
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], doc.stored_name)
    Grant.query.filter_by(document_id=doc.id).delete()
    db.session.delete(doc)
    db.session.commit()
    if os.path.isfile(path):
        os.remove(path)
    log_event("delete", "success", "document", doc_id)
    return redirect(url_for("docs.index"))


@docs.route("/<int:doc_id>/grant", methods=["POST"])
@login_required
def grant(doc_id):
    doc = get_doc(doc_id, "share")
    email = request.form.get("email", "").strip().lower()
    level = request.form.get("level")
    target = User.query.filter_by(email=email, active=True).first()
    if target is None or level not in ("read", "edit") or target.id == current_user.id:
        flash("Invalid user or level.", "error")
    else:
        g = Grant.query.filter_by(document_id=doc.id, user_id=target.id).first()
        if g is None:
            g = Grant(document_id=doc.id, user_id=target.id, level=level)
            db.session.add(g)
        g.level = level
        db.session.commit()
        log_event("grant", "success", "document", doc.id, details=f"{email} {level}")
    return redirect(url_for("docs.detail", doc_id=doc.id))


@docs.route("/<int:doc_id>/revoke/<int:user_id>", methods=["POST"])
@login_required
def revoke(doc_id, user_id):
    doc = get_doc(doc_id, "share")
    Grant.query.filter_by(document_id=doc.id, user_id=user_id).delete()
    db.session.commit()
    log_event("revoke", "success", "document", doc.id, details=f"user {user_id}")
    return redirect(url_for("docs.detail", doc_id=doc.id))