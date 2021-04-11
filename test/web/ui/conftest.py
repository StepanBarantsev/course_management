from test.web.ui.application import Application
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

fixture = None
session_fixture = None


@pytest.fixture()
def app():
    global fixture

    if fixture is None:
        fixture = Application()

    # fixture.login_page.login()

    return fixture


@pytest.fixture()
def session():
    global session_fixture

    if session_fixture is None:
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
        Session = sessionmaker(bind=engine)
        session_fixture = Session()

    return session_fixture


@pytest.fixture(scope='session', autouse=True)
def stop(request):
    def teardown():
        if fixture is not None:
            fixture.wd.quit()
        if session is not None:
            session_fixture.close()

    request.addfinalizer(teardown)
    return fixture
