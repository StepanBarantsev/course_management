from web.app.models import User, Course
from test.web.unit.helpers import create_default_user, login, logout, create_default_course, \
    add_default_student, add_default_check
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

    # Такой же lms_id как в 1 курсе
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

    # Данные пересекаются со 2 курсом
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


def test_create_student_success(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]

    student_dict = dict(email='stepan.barantsev@gmail.com', lms_id=10622, days=0)

    response = add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict)
    students = course.get_all_not_deleted_students().all()
    first_student = students[0]

    assert response.status == '302 FOUND'
    assert len(students) == 1
    assert first_student.email == student_dict['email']
    assert first_student.lms_id == student_dict['lms_id']
    assert first_student.number_of_days == student_dict['days']
    assert first_student.status == 'active'
    assert not first_student.deleted
    assert first_student.course_id == course.id
    assert first_student.telegram_id is None
    assert first_student.cert_link is None
    # Они автоматически тянутся из другой системы, так что просто проверяем что поля заполняются
    assert first_student.name is not None
    assert first_student.lms_email is not None
    assert first_student.registration_code is not None


def test_create_student_unsuccess(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]

    student_dict_1 = dict(email='stepan.barantsev@gmail.com', lms_id=10622, days=0)
    student_dict_2 = dict(email='stepan.barantsev2@gmail.com', lms_id=10622, days=0)

    add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict_1)
    response = add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict_2)
    students = course.get_all_not_deleted_students().all()
    first_student = students[0]

    assert response.status == '200 OK'
    assert len(students) == 1
    assert first_student.email == student_dict_1['email']
    assert first_student.lms_id == student_dict_1['lms_id']
    assert first_student.number_of_days == student_dict_1['days']
    assert first_student.status == 'active'
    assert not first_student.deleted
    assert first_student.course_id == course.id
    assert first_student.telegram_id is None
    assert first_student.cert_link is None
    # Они автоматически тянутся из другой системы, так что просто проверяем что поля заполняются
    assert first_student.name is not None
    assert first_student.lms_email is not None
    assert first_student.registration_code is not None


def test_edit_student_success(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]

    student_dict_1 = dict(email='stepan.barantsev@gmail.com', lms_id=10622, days=0)
    student_dict_new = dict(email='stepan.barantsev2@gmail.com', lms_id=1, days=35)

    add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict_1)

    first_student = course.get_all_not_deleted_students().all()[0]

    response = app['client'].post(f'/students/edit?course_id={course.id}&student_id={first_student.id}', data=student_dict_new)

    students = course.get_all_not_deleted_students().all()
    first_student = students[0]

    assert response.status == '302 FOUND'
    assert len(students) == 1
    assert first_student.email == student_dict_new['email']
    assert first_student.lms_id == student_dict_new['lms_id']
    assert first_student.number_of_days == student_dict_new['days']
    assert first_student.status == 'active'
    assert not first_student.deleted
    assert first_student.course_id == course.id
    assert first_student.telegram_id is None
    assert first_student.cert_link is None
    # Они автоматически тянутся из другой системы, так что просто проверяем что поля заполняются
    assert first_student.name is not None
    assert first_student.lms_email is not None
    assert first_student.registration_code is not None


def test_edit_student_unsuccess(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]

    student_dict_1 = dict(email='stepan.barantsev@gmail.com', lms_id=10622, days=0)
    student_dict_2 = dict(email='stepan.barantsev2@gmail.com', lms_id=1, days=0)
    student_dict_new = dict(email='stepan.barantsev3@gmail.com', lms_id=1, days=35)

    add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict_1)
    add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict_2)

    students = course.get_all_not_deleted_students().all()
    first_student = students[0]

    assert len(students) == 2

    response = app['client'].post(f'/students/edit?course_id={course.id}&student_id={first_student.id}', data=student_dict_new)

    assert response.status == '200 OK'
    assert len(students) == 2
    assert first_student.email == student_dict_1['email']
    assert first_student.lms_id == student_dict_1['lms_id']
    assert first_student.number_of_days == student_dict_1['days']
    assert first_student.status == 'active'
    assert not first_student.deleted
    assert first_student.course_id == course.id
    assert first_student.telegram_id is None
    assert first_student.cert_link is None
    # Они автоматически тянутся из другой системы, так что просто проверяем что поля заполняются
    assert first_student.name is not None
    assert first_student.lms_email is not None
    assert first_student.registration_code is not None


def test_add_check_success(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id)
    first_student = course.get_all_not_deleted_students().all()[0]
    block = course.get_block_by_num(1)

    check_dict = dict(
        block_number=1,
        link='http://check_link',
        amount=3000,
        is_first_payment=True
    )

    response = add_default_check(app['client'], first_student.id, check_dict)

    checks = first_student.get_all_not_deleted_checks().all()
    first_check = checks[0]

    assert response.status == '302 FOUND'
    assert len(checks) == 1
    assert first_check.link == check_dict['link']
    assert first_check.amount == check_dict['amount']
    assert first_check.another is None
    assert first_check.block_id == block.id
    assert first_check.student_id == first_student.id
    assert not first_check.deleted


def test_add_check_unsuccess(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id)
    first_student = course.get_all_not_deleted_students().all()[0]
    block = course.get_block_by_num(1)

    check_dict_1 = dict(
        block_number=1,
        link='http://check_link',
        amount=3000,
        is_first_payment=True
    )

    check_dict_2 = dict(
        block_number=1,
        link='http://check_link_2',
        amount=30003,
        is_first_payment=False
    )

    add_default_check(app['client'], first_student.id, check_dict_1)
    response = add_default_check(app['client'], first_student.id, check_dict_2)

    checks = first_student.get_all_not_deleted_checks().all()
    first_check = checks[0]

    assert response.status == '200 OK'
    assert len(checks) == 1
    assert first_check.link == check_dict_1['link']
    assert first_check.amount == check_dict_1['amount']
    assert first_check.another is None
    assert first_check.block_id == block.id
    assert first_check.student_id == first_student.id
    assert not first_check.deleted


def test_edit_check_success(app):
    course_dict = dict(
        name='Название курса',
        lms_id=1040,
        trainer_lms_id=1,
        trainer_telegram_id=271828,
        review_link='http://testlink',
        help_field='Информация отсутствует',
        default_number_of_days=30,
        number_homeworks=15,
        number_of_blocks=4,
        is_more_then_one_block=True
    )
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'], course_dict)
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id)
    first_student = course.get_all_not_deleted_students().all()[0]
    block_2 = course.get_block_by_num(2)

    check_dict_1 = dict(
        block_number=1,
        link='http://check_link',
        amount=3000,
        is_first_payment=True
    )

    check_dict_new = dict(
        block_number=2,
        link='http://check_link_3',
        amount=30003,
        is_first_payment=False
    )

    add_default_check(app['client'], first_student.id, check_dict_1)
    first_check = first_student.get_all_not_deleted_checks().all()[0]
    response = app['client'].post(f'/checks/edit?student_id={first_student.id}&check_id={first_check.id}', data=check_dict_new)

    checks = first_student.get_all_not_deleted_checks().all()
    first_check = checks[0]

    assert response.status == '302 FOUND'
    assert len(checks) == 1
    assert first_check.link == check_dict_new['link']
    assert first_check.amount == check_dict_new['amount']
    assert first_check.another is None
    assert first_check.block_id == block_2.id
    assert first_check.student_id == first_student.id
    assert not first_check.deleted


def test_edit_check_unsuccess(app):
    course_dict = dict(
        name='Название курса',
        lms_id=1040,
        trainer_lms_id=1,
        trainer_telegram_id=271828,
        review_link='http://testlink',
        help_field='Информация отсутствует',
        default_number_of_days=30,
        number_homeworks=15,
        number_of_blocks=4,
        is_more_then_one_block=True
    )
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'], course_dict)
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id)
    first_student = course.get_all_not_deleted_students().all()[0]
    block = course.get_block_by_num(1)

    check_dict_1 = dict(
        block_number=1,
        link='http://check_link',
        amount=3000,
        is_first_payment=True
    )

    check_dict_2 = dict(
        block_number=2,
        link='http://check_link_2',
        amount=30002,
        is_first_payment=False
    )

    check_dict_new = dict(
        block_number=2,
        link='http://check_link_3',
        amount=30003,
        is_first_payment=False
    )

    add_default_check(app['client'], first_student.id, check_dict_1)
    add_default_check(app['client'], first_student.id, check_dict_2)
    first_check = first_student.get_all_not_deleted_checks().all()[0]
    response = app['client'].post(f'/checks/edit?student_id={first_student.id}&check_id={first_check.id}', data=check_dict_new)

    checks = first_student.get_all_not_deleted_checks().all()
    first_check = checks[0]

    assert response.status == '200 OK'
    assert len(checks) == 2
    assert first_check.link == check_dict_1['link']
    assert first_check.amount == check_dict_1['amount']
    assert first_check.another is None
    assert first_check.block_id == block.id
    assert first_check.student_id == first_student.id
    assert not first_check.deleted


def test_edit_profile_success(app):
    username = 'testUser'
    password = '123'

    create_default_user(app['db'], username, password)
    login(app['client'], username, password)

    profile_dict = dict(
        username="Username",
        email='stepan.barantsev@gmail.com',
        name='Имя Фамилия',
        lms_id=10622,
        telegram_id=23782378,
        telegram_nickname='Bars'
    )

    response = app['client'].post(f'/editprofile', data=profile_dict)

    users = User.get_all_users()
    user = users[0]

    assert response.status == '302 FOUND'
    assert len(users) == 1
    assert user.username == profile_dict['username']
    assert user.email == profile_dict['email']
    assert user.name == profile_dict['name']
    assert user.telegram_id == profile_dict['telegram_id']
    assert user.telegram_nickname == profile_dict['telegram_nickname']
    assert user.lms_id == profile_dict['lms_id']
    assert not user.flag_emails_from_default_mail
    assert user.flag_is_messages_from_bot_is_delivered


def test_edit_profile_unsuccess(app):
    username_1 = 'testUser'
    password_1 = '123'
    email_1 = 'testmail@gmail.com'

    username_2 = 'testUser2'
    password_2 = '123'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2)
    login(app['client'], username_1, password_1)

    profile_dict = dict(
        username=username_2,
        email='stepan.barantsev@gmail.com',
        name='Имя Фамилия',
        lms_id=10622,
        telegram_id=23782378,
        telegram_nickname='Bars'
    )

    response = app['client'].post('/editprofile', data=profile_dict)

    users = User.get_all_users()
    user = users[0]

    assert response.status == '200 OK'
    assert len(users) == 2
    assert user.username == username_1
    assert user.email == email_1
    assert user.name is None
    assert user.telegram_id is None
    assert user.telegram_nickname is None
    assert user.lms_id is None
    assert not user.flag_emails_from_default_mail
    assert user.flag_is_messages_from_bot_is_delivered


def test_trainer_try_to_edit_anothers_student(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    student_dict_1 = dict(email='stepan.barantsev@gmail.com', lms_id=10622, days=0)
    student_dict_new = dict(email='stepan.barantsev3@gmail.com', lms_id=1, days=35)

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id, data_dict=student_dict_1)
    student = course.get_all_not_deleted_students()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/students/edit?course_id={course.id}&student_id={student.id}', data=student_dict_new)

    assert response.status == '403 FORBIDDEN'
    assert student.email == student_dict_1['email']
    assert student.lms_id == student_dict_1['lms_id']
    assert student.number_of_days == student_dict_1['days']


def test_trainer_try_to_add_student_to_anothers_course(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = add_default_student(client=app['client'], course_id=course.id)
    students = course.get_all_not_deleted_students().all()

    assert response.status == '403 FORBIDDEN'
    assert len(students) == 0


def test_trainer_try_to_edit_check_to_anothers_student(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id)
    student = course.get_all_not_deleted_students()[0]
    add_default_check(app['client'], student.id)
    check = student.get_all_not_deleted_checks()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/checks/edit?check_id={check.id}&student_id={student.id}', data=dict())

    assert response.status == '403 FORBIDDEN'


def test_trainer_try_edit_additional_anothers_course_settings(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/coursecreate/edit_additional?course_id={course.id}', data=dict())

    assert response.status == '403 FORBIDDEN'


def test_trainer_try_edit_anothers_course(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/coursecreate/edit?course_id={course.id}', data=dict())

    assert response.status == '403 FORBIDDEN'


def test_trainer_try_to_add_check_to_anothers_student(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(client=app['client'], course_id=course.id)
    student = course.get_all_not_deleted_students()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = add_default_check(app['client'], student.id)
    checks = student.get_all_not_deleted_checks().all()

    assert response.status == '403 FORBIDDEN'
    assert len(checks) == 0


def test_trainer_try_delete_anothers_course(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/coursecreate/delete', data=dict(course_id=course.id))
    courses = Course.get_all_not_deleted_courses().all()

    assert response.status == '403 FORBIDDEN'
    assert len(courses) == 1


def test_trainer_try_delete_anothers_student(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(app['client'], course.id)
    student = course.get_all_not_deleted_students()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/students/delete', data=dict(student_id=student.id, course_id=course.id))
    students = course.get_all_not_deleted_students().all()

    assert response.status == '403 FORBIDDEN'
    assert len(students) == 1


def test_trainer_try_delete_anothers_check(app):
    username_1 = 'testUser1'
    password_1 = '123'
    email_1 = 'email_1'

    username_2 = 'testUser2'
    password_2 = '123'
    email_2 = 'email_2'

    create_default_user(app['db'], username_1, password_1, email_1)
    create_default_user(app['db'], username_2, password_2, email_2)

    login(app['client'], username_1, password_1)
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(app['client'], course.id)
    student = course.get_all_not_deleted_students()[0]
    add_default_check(app['client'], student.id)
    check = student.get_all_not_deleted_checks()[0]
    logout(app['client'])
    login(app['client'], username_2, password_2)
    response = app['client'].post(f'/checks/delete', data=dict(student_id=student.id, check_id=check.id))
    checks = student.get_all_not_deleted_checks().all()

    assert response.status == '403 FORBIDDEN'
    assert len(checks) == 1


def test_delete_course(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    response = app['client'].post(f'/coursecreate/delete', data=dict(course_id=course.id))
    courses = Course.get_all_not_deleted_courses().all()

    assert response.status == '302 FOUND'
    assert len(courses) == 0


def test_delete_student(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(app['client'], course.id)
    student = course.get_all_not_deleted_students()[0]

    response = app['client'].post(f'/students/delete', data=dict(course_id=course.id, student_id=student.id))
    students = course.get_all_not_deleted_students().all()

    assert response.status == '302 FOUND'
    assert len(students) == 0


def test_delete_check(app):
    create_default_user(app['db'])
    login(app['client'])
    create_default_course(app['client'])
    course = Course.get_all_not_deleted_courses()[0]
    add_default_student(app['client'], course.id)
    student = course.get_all_not_deleted_students()[0]
    add_default_check(app['client'], student.id)
    check = student.get_all_not_deleted_checks()[0]

    response = app['client'].post(f'/checks/delete', data=dict(check_id=check.id, student_id=student.id))
    checks = student.get_all_not_deleted_checks().all()

    assert response.status == '302 FOUND'
    assert len(checks) == 0
