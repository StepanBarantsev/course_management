from web.app.models import User
from werkzeug.security import generate_password_hash


def login(client, username, password):
    response = client.post('/auth/login', data=dict(
        username=username,
        password=password,
    ))

    return response


def logout(client):
    return client.get('/auth/logout')


def create_default_user(db, name, password, email='default@gmail.com'):
    user = User(username=name, password_hash=generate_password_hash(password), email=email)
    db.session.add(user)
    db.session.commit()
