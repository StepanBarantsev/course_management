from web.app.models import User
from test.web.unit.helpers import create_default_user, login, logout
from flask_login import current_user


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
    response = login(app['client'], username, password)

    assert response.status == '302 FOUND'
    assert '/auth/login' not in response.headers['location']
    assert '/index' in response.headers['location']
    assert current_user.is_authenticated


def test_auth_unsuccess(app):

    username = 'testUser'
    password = '123'
    incorrect_password = '123123'

    create_default_user(app['db'], username, password)
    response = login(app['client'], username, incorrect_password)

    assert response.status == '302 FOUND'
    assert '/auth/login' in response.headers['location']
    assert not current_user.is_authenticated


def test_auth_logout(app):

    username = 'testUser'
    password = '123'

    create_default_user(app['db'], username, password)
    login(app['client'], username, password)
    response = logout(app['client'])

    assert response.status == '302 FOUND'
    assert '/auth/login' in response.headers['location']
    assert not current_user.is_authenticated


def test_reset_password_success(app):

    username = 'testUser'
    old_password = '123'
    new_password = '321'

    create_default_user(app['db'], username, old_password)
    login(app['client'], username, old_password)

    response = app['client'].post('/reset_password', data=dict(
        old_password=old_password,
        new_password=new_password,
        repeated_password=new_password
    ))

    assert response.status == "302 FOUND"

    logout(app['client'])
    login(app['client'], username, old_password)
    assert not current_user.is_authenticated

    login(app['client'], username, new_password)
    assert current_user.is_authenticated


def test_reset_password_unsuccess(app):

    username = 'testUser'
    old_password = '123'
    incorrect_old_password = 'incorrect'
    new_password = '321'

    create_default_user(app['db'], username, old_password)
    login(app['client'], username, old_password)

    response = app['client'].post('/reset_password', data=dict(
        old_password=incorrect_old_password,
        new_password=new_password,
        repeated_password=new_password
    ))

    assert response.status == "200 OK"

    logout(app['client'])
    login(app['client'], username, new_password)
    assert not current_user.is_authenticated

    login(app['client'], username, old_password)
    assert current_user.is_authenticated