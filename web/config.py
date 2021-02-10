import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = True if os.environ.get('MAIL_USE_TLS') == 'True' else False
    MAIL_USE_SSL = True if os.environ.get('MAIL_USE_SSL') == 'True' else False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMIN')]
    SECURITY_EMAIL_SENDER = os.environ.get('ADMIN')

    ELEMENTS_PER_PAGE = 10
    DEFAULT_NUM_OF_DAYS = 30
    CODE_FOR_REGISTRATION = os.environ.get('CODE_FOR_REGISTRATION')
