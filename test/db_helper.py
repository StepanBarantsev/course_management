from web.app.models import User
from werkzeug.security import generate_password_hash


def create_minimal_user(session):
    user = User(username='Stepan', email='stepan.barantsev@gmail.com', password_hash=generate_password_hash('1'))
    session.add(user)
    session.commit()