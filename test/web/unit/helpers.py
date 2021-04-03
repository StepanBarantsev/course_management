from web.app.models import User
from werkzeug.security import generate_password_hash


def login(client, username, password):
    pass


def logout(client):
    pass


def create_default_user(db, name, password, email='default@gmail.com'):
    user = User(username=name, password_hash=generate_password_hash(password), email=email)
    db.session.add(user)
    db.session.commit()
