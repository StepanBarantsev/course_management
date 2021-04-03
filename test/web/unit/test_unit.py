from web.app.models import User
from test.web.unit.helpers import create_default_user


def test_registration_success(app):

    username = 'testUser'
    email = 'testmail@gmail.com'

    response = app['client'].post('/auth/register', data=dict(
                username=username,
                email=email,
                password='123',
                password2='123',
                registration_code=app['app'].config['CODE_FOR_REGISTRATION']
            ), follow_redirects=True)

    users = User.get_all_users()
    user = users[0]

    assert response.status == '200 OK'
    assert len(users) == 1
    assert user.username == username
    assert user.email == email
    assert user.name is None
    assert user.telegram_id is None
    assert user.telegram_nickname is None
    assert user.lms_id is None
    assert user.flag_emails_from_default_mail is False
    assert user.flag_is_messages_from_bot_is_delivered is True


def test_registration_fail(app):

    username = 'testUser'
    email = 'testmail@gmail.com'

    response = app['client'].post('/auth/register', data=dict(
                username=username,
                email=email,
                password='123',
                password2='123',
                registration_code='incorrectCode'
            ), follow_redirects=True)

    users = User.get_all_users()

    assert response.status == '403 FORBIDDEN'
    assert len(users) == 0


def test_auth_success(app):

    username = 'testUser'
    password = '123'

    create_default_user(app['db'], username, password)

    response = app['client'].post('/auth/login', data=dict(
                username=username,
                password=password,
            ), follow_redirects=True)

    assert response.status == '200 OK'
