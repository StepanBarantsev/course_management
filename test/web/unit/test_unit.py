from web.app.models import User, Course
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


def test_add_new_course_success(app):

    create_default_user(app['db'])
    login(app['client'])

    name = 'Название курса'
    lms_id = 1040
    trainer_lms_id = 1
    trainer_telegram_id = 271828
    review_link = 'http://testlink'
    help_field = 'Информация отсутствует'
    default_number_of_days = 30
    number_homeworks = 15
    # Если None, то в бд идет 1
    number_of_blocks = None

    response = app['client'].post('/coursecreate/create', data=dict(
        name=name,
        lms_id=lms_id,
        trainer_lms_id=trainer_lms_id,
        trainer_telegram_id=trainer_telegram_id,
        review_link=review_link,
        help_field=help_field,
        default_number_of_days=default_number_of_days,
        number_homeworks=number_homeworks,
        number_of_blocks=number_of_blocks,
    ))

    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert response.status == "302 FOUND"
    assert len(courses) == 1
    assert first_course.name == name
    assert not first_course.deleted
    assert first_course.lms_id == lms_id
    assert first_course.trainer_telegram_id == trainer_telegram_id
    assert first_course.trainer_lms_id == trainer_lms_id
    assert first_course.num_of_blocks == 1
    assert first_course.number_of_homeworks == number_homeworks
    assert first_course.default_num_days == default_number_of_days
    assert first_course.review_link == review_link
    assert first_course.help == help_field
    assert first_course.user_id == current_user.id
    assert not first_course.is_certificate_needed


def test_create_new_course_unsuccess(app):

    create_default_user(app['db'])
    login(app['client'])

    name_1 = 'Название курса'
    lms_id_1 = 1040
    trainer_lms_id_1 = 1
    trainer_telegram_id_1 = 271828
    review_link_1 = 'http://testlink'
    help_field_1 = 'Информация отсутствует'
    default_number_of_days_1 = 30
    number_homeworks_1 = 15
    number_of_blocks_1 = None

    response_1 = app['client'].post('/coursecreate/create', data=dict(
        name=name_1,
        lms_id=lms_id_1,
        trainer_lms_id=trainer_lms_id_1,
        trainer_telegram_id=trainer_telegram_id_1,
        review_link=review_link_1,
        help_field=help_field_1,
        default_number_of_days=default_number_of_days_1,
        number_homeworks=number_homeworks_1,
        number_of_blocks=number_of_blocks_1,
    ))

    courses = Course.get_all_not_deleted_courses().all()

    assert response_1.status == "302 FOUND"
    assert len(courses) == 1

    name_2 = 'Название курса 2'
    # Такой же Lms_id
    lms_id_2 = 1040
    trainer_lms_id_2 = 2
    trainer_telegram_id_2 = 2718282
    review_link_2 = 'http://testlink_2'
    help_field_2 = 'Информация отсутствует'
    default_number_of_days_2 = 30
    number_homeworks_2 = 15
    number_of_blocks_2 = None

    response_2 = app['client'].post('/coursecreate/create', data=dict(
        name=name_2,
        lms_id=lms_id_2,
        trainer_lms_id=trainer_lms_id_2,
        trainer_telegram_id=trainer_telegram_id_2,
        review_link=review_link_2,
        help_field=help_field_2,
        default_number_of_days=default_number_of_days_2,
        number_homeworks=number_homeworks_2,
        number_of_blocks=number_of_blocks_2,
    ))

    courses = Course.get_all_not_deleted_courses().all()

    assert response_2.status == "200 OK"
    assert len(courses) == 1


def test_edit_course_success(app):

    create_default_user(app['db'])
    login(app['client'])

    name = 'Название курса'
    lms_id = 1040
    trainer_lms_id = 1
    trainer_telegram_id = 271828
    review_link = 'http://testlink'
    help_field = 'Информация отсутствует'
    default_number_of_days = 30
    number_homeworks = 15
    number_of_blocks = None

    app['client'].post('/coursecreate/create', data=dict(
        name=name,
        lms_id=lms_id,
        trainer_lms_id=trainer_lms_id,
        trainer_telegram_id=trainer_telegram_id,
        review_link=review_link,
        help_field=help_field,
        default_number_of_days=default_number_of_days,
        number_homeworks=number_homeworks,
        number_of_blocks=number_of_blocks,
    ))

    first_course = Course.get_all_not_deleted_courses()[0]

    new_name = 'Новое название курса'
    new_lms_id = 1041
    new_trainer_lms_id = 2
    new_trainer_telegram_id = 333
    new_review_link = 'http://testlink_new'
    new_help_field = 'Информация отсутствует новая'
    new_default_number_of_days = 301
    new_number_homeworks = 151
    new_number_of_blocks = 4

    response = app['client'].post(f'/coursecreate/edit?course_id={first_course.id}', data=dict(
        name=new_name,
        lms_id=new_lms_id,
        trainer_lms_id=new_trainer_lms_id,
        trainer_telegram_id=new_trainer_telegram_id,
        review_link=new_review_link,
        help_field=new_help_field,
        default_number_of_days=new_default_number_of_days,
        number_homeworks=new_number_homeworks,
        number_of_blocks=new_number_of_blocks,
        is_more_then_one_block=True
    ))

    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert response.status == "302 FOUND"
    assert len(courses) == 1
    assert first_course.name == new_name
    assert not first_course.deleted
    assert first_course.lms_id == new_lms_id
    assert first_course.trainer_telegram_id == new_trainer_telegram_id
    assert first_course.trainer_lms_id == new_trainer_lms_id
    assert first_course.num_of_blocks == new_number_of_blocks
    assert first_course.number_of_homeworks == new_number_homeworks
    assert first_course.default_num_days == new_default_number_of_days
    assert first_course.review_link == new_review_link
    assert first_course.help == new_help_field
    assert first_course.user_id == current_user.id
    assert not first_course.is_certificate_needed


def test_edit_course_unsuccess(app):
    create_default_user(app['db'])
    login(app['client'])

    name_1 = 'Название курса'
    lms_id_1 = 1040
    trainer_lms_id_1 = 1
    trainer_telegram_id_1 = 271828
    review_link_1 = 'http://testlink'
    help_field_1 = 'Информация отсутствует'
    default_number_of_days_1 = 30
    number_homeworks_1 = 15
    number_of_blocks_1 = None

    app['client'].post('/coursecreate/create', data=dict(
        name=name_1,
        lms_id=lms_id_1,
        trainer_lms_id=trainer_lms_id_1,
        trainer_telegram_id=trainer_telegram_id_1,
        review_link=review_link_1,
        help_field=help_field_1,
        default_number_of_days=default_number_of_days_1,
        number_homeworks=number_homeworks_1,
        number_of_blocks=number_of_blocks_1,
    ))

    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert len(courses) == 1

    name_2 = 'Название курса 2'
    lms_id_2 = 10401
    trainer_lms_id_2 = 2
    trainer_telegram_id_2 = 2718282
    review_link_2 = 'http://testlink_2'
    help_field_2 = 'Информация отсутствует'
    default_number_of_days_2 = 30
    number_homeworks_2 = 15
    number_of_blocks_2 = None

    app['client'].post('/coursecreate/create', data=dict(
        name=name_2,
        lms_id=lms_id_2,
        trainer_lms_id=trainer_lms_id_2,
        trainer_telegram_id=trainer_telegram_id_2,
        review_link=review_link_2,
        help_field=help_field_2,
        default_number_of_days=default_number_of_days_2,
        number_homeworks=number_homeworks_2,
        number_of_blocks=number_of_blocks_2,
    ))

    courses = Course.get_all_not_deleted_courses().all()

    assert len(courses) == 2

    new_name = 'Новое название курса'
    # Меняем на существующий Lms Id
    new_lms_id = 10401
    new_trainer_lms_id = 2
    new_trainer_telegram_id = 333
    new_review_link = 'http://testlink_new'
    new_help_field = 'Информация отсутствует новая'
    new_default_number_of_days = 301
    new_number_homeworks = 151
    new_number_of_blocks = 4

    response = app['client'].post(f'/coursecreate/edit?course_id={first_course.id}', data=dict(
        name=new_name,
        lms_id=new_lms_id,
        trainer_lms_id=new_trainer_lms_id,
        trainer_telegram_id=new_trainer_telegram_id,
        review_link=new_review_link,
        help_field=new_help_field,
        default_number_of_days=new_default_number_of_days,
        number_homeworks=new_number_homeworks,
        number_of_blocks=new_number_of_blocks,
    ))

    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert response.status == "200 OK"
    assert len(courses) == 2
    assert first_course.name == name_1
    assert not first_course.deleted
    assert first_course.lms_id == lms_id_1
    assert first_course.trainer_telegram_id == trainer_telegram_id_1
    assert first_course.trainer_lms_id == trainer_lms_id_1
    assert first_course.num_of_blocks == 1
    assert first_course.number_of_homeworks == number_homeworks_1
    assert first_course.default_num_days == default_number_of_days_1
    assert first_course.review_link == review_link_1
    assert first_course.help == help_field_1
    assert first_course.user_id == current_user.id
    assert not first_course.is_certificate_needed

