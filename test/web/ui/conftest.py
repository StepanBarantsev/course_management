from test.web.ui.application import Application
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from web.app.models import User
from werkzeug.security import generate_password_hash


fixture = None
session_fixture = None


@pytest.fixture()
def session():
    global session_fixture

    if session_fixture is None:
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
        Session = sessionmaker(bind=engine)
        session_fixture = Session()
        session_fixture.query(User).delete()
        session_fixture.commit()

    return session_fixture


@pytest.fixture()
def app():
    global fixture

    if fixture is None:
        fixture = Application()

    fixture.open_base_page()
    user = User(username='Stepan', email='stepan.barantsev@gmail.com', password_hash=generate_password_hash('1'))
    session_fixture.add(user)
    session_fixture.commit()
    fixture.login_page.login('Stepan', '1')

    return fixture


@pytest.fixture(scope='session', autouse=True)
def stop(request):
    def teardown():
        if fixture is not None:
            fixture.wd.quit()
        if session is not None:
            session_fixture.close()

    request.addfinalizer(teardown)
