import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ADMINS = [os.environ.get('ADMIN')]
    SECURITY_EMAIL_SENDER = os.environ.get('ADMIN')

    ELEMENTS_PER_PAGE = 10
    DEFAULT_NUM_OF_DAYS = 30
    CODE_FOR_REGISTRATION = os.environ.get('CODE_FOR_REGISTRATION')
