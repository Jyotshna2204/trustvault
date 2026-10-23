from app import create_app
from app.extensions import db
from app.models import User

DEMO = [
    ("admin@trustvault.test", "Alice Admin", "admin", "Demo-Admin-2026"),
    ("owner1@trustvault.test", "Oscar Owner", "owner", "Demo-Owner1-2026"),
    ("owner2@trustvault.test", "Olivia Owner", "owner", "Demo-Owner2-2026"),
    ("viewer@trustvault.test", "Victor Viewer", "viewer", "Demo-Viewer-2026"),
]

app = create_app()
with app.app_context():
    db.create_all()
    for email, name, role, password in DEMO:
        if not User.query.filter_by(email=email).first():
            user = User(email=email, name=name, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print("created", email)