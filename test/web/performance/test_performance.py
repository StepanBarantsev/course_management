from locust import HttpUser, TaskSet, task
import os
from web.app.models import User, Course
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time


class WebsiteUser(HttpUser):

    USER_CREDENTIALS = [("Stepan" + str(i), f"stepan{i}@gmail.com", "123") for i in range(100)]
    COURSE_CREDITIONALS = [("Stepan" + str(i), 1 + i) for i in range(500)]

    def on_start(self):
        registration_code = os.getenv("CODE_FOR_REGISTRATION")
        username, email, password = self.USER_CREDENTIALS.pop()

        self.client.post("/auth/register",
                         {"username": username,
                          "email": email,
                          "password": password,
                          "password2": password,
                          "registration_code": registration_code})

        self.client.post('/auth/login', data=dict(
            username=username,
            password=password,
        ))

        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def teardown(self):
        self.session.query(Course).delete()
        self.session.query(User).delete()
        self.session.commit()

    @task
    def create_course(self):
        name, lms_id = self.COURSE_CREDITIONALS.pop()
        course_dict = dict(
            name=name,
            lms_id=lms_id,
            trainer_lms_id=1,
            trainer_telegram_id=271828,
            review_link='http://testlink',
            help_field='Информация отсутствует',
            default_number_of_days=30,
            number_homeworks=15,
            number_of_blocks=None
        )

        self.client.post('/coursecreate/create', course_dict)

    @task
    def get_main(self):
        self.client.get('/')

    @task
    def get_profile(self):
        self.client.get('/profile')
