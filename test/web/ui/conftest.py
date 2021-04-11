from test.web.ui.application import Application
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from web.app.models import User, Course
from test.db_helper import create_minimal_user, create_full_info_user


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

    session_fixture.query(Course).delete()
    session_fixture.query(User).delete()
    session_fixture.commit()

    return session_fixture


@pytest.fixture()
def app():
    global fixture

    if fixture is None:
        fixture = Application()

    return fixture


@pytest.fixture()
def user_logined_minimal():
    global fixture

    fixture.open_base_page()
    user = create_minimal_user(session_fixture)
    fixture.login_page.login('Stepan', '1')

    return user


@pytest.fixture()
def user_logined():
    global fixture

    fixture.open_base_page()
    user = create_full_info_user(session_fixture)
    fixture.login_page.login('Stepan', '1')

    return user


@pytest.fixture(scope='session', autouse=True)
def stop(request):
    def teardown():
        if fixture is not None:
            fixture.wd.quit()
        if session is not None:
            session_fixture.close()

    request.addfinalizer(teardown)
