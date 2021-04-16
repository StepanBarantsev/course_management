from locust import HttpUser, TaskSet, task, between, constant
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
    def get_main(self):
        self.client.get('/')

    @task
    def get_profile(self):
        self.client.get('/profile')
