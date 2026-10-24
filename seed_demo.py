from app import create_app
from app.extensions import db
from app.models import User

DEMO = [
    ("admin@trustvault.test", "Jyotshna", "admin", "MyAdmin#2026"),
    ("owner1@trustvault.test", "Ruthika", "owner", "DemoOwner1#2026"),
    ("owner2@trustvault.test", "Sathvik", "owner", "Demo-Owner2-2026"),
    ("viewer@trustvault.test", "Saicharan", "viewer", "Demo-Viewer-2026"),
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