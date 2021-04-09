from web.app.models import User, Course
from test.web.unit.helpers import create_default_user, login, logout, create_default_course
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

    course_dict = dict(
        name='Название курса',
        lms_id=1040,
        trainer_lms_id=1,
        trainer_telegram_id=271828,
        review_link='http://testlink',
        help_field='Информация отсутствует',
        default_number_of_days=30,
        number_homeworks=15,
        number_of_blocks=None
    )

    response = create_default_course(app['client'], data_dict=course_dict)

    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert response.status == "302 FOUND"
    assert len(courses) == 1
    assert first_course.name == course_dict['name']
    assert not first_course.deleted
    assert first_course.lms_id == course_dict['lms_id']
    assert first_course.trainer_telegram_id == course_dict['trainer_telegram_id']
    assert first_course.trainer_lms_id == course_dict['trainer_lms_id']
    assert first_course.num_of_blocks == 1
    assert first_course.number_of_homeworks == course_dict['number_homeworks']
    assert first_course.default_num_days == course_dict['default_number_of_days']
    assert first_course.review_link == course_dict['review_link']
    assert first_course.help == course_dict['help_field']
    assert first_course.user_id == current_user.id
    assert not first_course.is_certificate_needed


def test_create_new_course_unsuccess(app):

    create_default_user(app['db'])
    login(app['client'])

    course_dict_1 = dict(
        name='Название курса',
        lms_id=1040,
        trainer_lms_id=1,
        trainer_telegram_id=271828,
        review_link='http://testlink',
        help_field='Информация отсутствует',
        default_number_of_days=30,
        number_homeworks=15,
        number_of_blocks=None
    )

    course_dict_2 = dict(
        name='Название курса 2',
        lms_id=1040,
        trainer_lms_id=2,
        trainer_telegram_id=2718282,
        review_link='http://testlink_2',
        help_field='Информация отсутствует 2',
        default_number_of_days=302,
        number_homeworks=152,
        number_of_blocks=None
    )

    response_1 = create_default_course(app['client'], course_dict_1)
    courses = Course.get_all_not_deleted_courses().all()

    assert response_1.status == "302 FOUND"
    assert len(courses) == 1

    response_2 = create_default_course(app['client'], course_dict_2)
    courses = Course.get_all_not_deleted_courses().all()

    assert response_2.status == "200 OK"
    assert len(courses) == 1


def test_edit_course_success(app):

    create_default_user(app['db'])
    login(app['client'])

    course_dict_1 = dict(
        name='Название курса',
        lms_id=1040,
        trainer_lms_id=1,
        trainer_telegram_id=271828,
        review_link='http://testlink',
        help_field='Информация отсутствует',
        default_number_of_days=30,
        number_homeworks=15,
        number_of_blocks=None
    )

    course_dict_new = dict(
        name='Новое название курса',
        lms_id=1041,
        trainer_lms_id=2,
        trainer_telegram_id=333,
        review_link='http://testlink_new',
        help_field='Новая информация отсутствует',
        default_number_of_days=303,
        number_homeworks=151,
        number_of_blocks=4,
        is_more_then_one_block=True
    )

    create_default_course(app['client'], course_dict_1)
    first_course = Course.get_all_not_deleted_courses()[0]

    response = app['client'].post(f'/coursecreate/edit?course_id={first_course.id}', data=course_dict_new)

    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert response.status == "302 FOUND"
    assert len(courses) == 1
    assert first_course.name == course_dict_new['name']
    assert not first_course.deleted
    assert first_course.lms_id == course_dict_new['lms_id']
    assert first_course.trainer_telegram_id == course_dict_new['trainer_telegram_id']
    assert first_course.trainer_lms_id == course_dict_new['trainer_lms_id']
    assert first_course.num_of_blocks == course_dict_new['number_of_blocks']
    assert first_course.number_of_homeworks == course_dict_new['number_homeworks']
    assert first_course.default_num_days == course_dict_new['default_number_of_days']
    assert first_course.review_link == course_dict_new['review_link']
    assert first_course.help == course_dict_new['help_field']
    assert first_course.user_id == current_user.id
    assert not first_course.is_certificate_needed


def test_edit_course_unsuccess(app):
    create_default_user(app['db'])
    login(app['client'])

    course_dict_1 = dict(
        name='Название курса',
        lms_id=1040,
        trainer_lms_id=1,
        trainer_telegram_id=271828,
        review_link='http://testlink',
        help_field='Информация отсутствует',
        default_number_of_days=30,
        number_homeworks=15,
        number_of_blocks=None
    )

    course_dict_2 = dict(
        name='Название курса 2',
        lms_id=1041,
        trainer_lms_id=2,
        trainer_telegram_id=2718282,
        review_link='http://testlink_2',
        help_field='Информация отсутствует 2',
        default_number_of_days=302,
        number_homeworks=152,
        number_of_blocks=None
    )

    course_dict_new = dict(
        name='Новое название курса',
        lms_id=1041,
        trainer_lms_id=2,
        trainer_telegram_id=333,
        review_link='http://testlink_new',
        help_field='Новая информация отсутствует',
        default_number_of_days=303,
        number_homeworks=151,
        number_of_blocks=4,
        is_more_then_one_block=True
    )

    create_default_course(app['client'], course_dict_1)
    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert len(courses) == 1

    create_default_course(app['client'], course_dict_2)
    courses = Course.get_all_not_deleted_courses().all()

    assert len(courses) == 2

    response = app['client'].post(f'/coursecreate/edit?course_id={first_course.id}', data=course_dict_new)
    courses = Course.get_all_not_deleted_courses().all()
    first_course = courses[0]

    assert response.status == "200 OK"
    assert len(courses) == 2
    assert first_course.name == course_dict_1['name']
    assert not first_course.deleted
    assert first_course.lms_id == course_dict_1['lms_id']
    assert first_course.trainer_telegram_id == course_dict_1['trainer_telegram_id']
    assert first_course.trainer_lms_id == course_dict_1['trainer_lms_id']
    assert first_course.num_of_blocks == 1
    assert first_course.number_of_homeworks == course_dict_1['number_homeworks']
    assert first_course.default_num_days == course_dict_1['default_number_of_days']
    assert first_course.review_link == course_dict_1['review_link']
    assert first_course.help == course_dict_1['help_field']
    assert first_course.user_id == current_user.id
    assert not first_course.is_certificate_needed

