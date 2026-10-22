import secrets

from app import create_app
from app.extensions import db
from app.models import ROLE_ADMIN, ROLE_OWNER, ROLE_VIEWER, User

USERS = [
    ("admin@trustvault.test", "Alice Admin", ROLE_ADMIN),
    ("owner1@trustvault.test", "Oscar Owner", ROLE_OWNER),
    ("owner2@trustvault.test", "Olivia Owner", ROLE_OWNER),
    ("viewer@trustvault.test", "Victor Viewer", ROLE_VIEWER),
]

app = create_app()
with app.app_context():
    db.create_all()
    for email, name, role in USERS:
        if User.query.filter_by(email=email).first():
            print(f"exists:  {email}")
            continue
        password = secrets.token_urlsafe(12)
        user = User(email=email, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"created: {email}  password: {password}")