from web.app.models import User
from werkzeug.security import generate_password_hash


def login(client, username='def_name', password='def_pass'):
    response = client.post('/auth/login', data=dict(
        username=username,
        password=password,
    ))

    return response


def logout(client):
    return client.get('/auth/logout')


def create_default_user(db, name='def_name', password='def_pass', email='default@gmail.com'):
    user = User(username=name, password_hash=generate_password_hash(password), email=email)
    db.session.add(user)
    db.session.commit()


def create_default_course(client, data_dict=None):
    if data_dict is None:
        data_dict = dict(
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
    return client.post('/coursecreate/create', data=data_dict)


def add_default_student(client, course_id, data_dict=None):
    if data_dict is None:
        data_dict = dict(
            email='stepan.barantsev@gmail.com',
            lms_id=10622,
            days=0
        )
    return client.post(f'/students/add?course_id={course_id}', data=data_dict)


def add_default_check(client, student_id, data_dict=None):
    if data_dict is None:
        data_dict = dict(
            block_number=1,
            link='http://check_link',
            amount=3000,
            is_first_payment=True
        )
    return client.post(f'/checks/add?student_id={student_id}', data=data_dict)

