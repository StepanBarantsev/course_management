import os


class ConfigTelegram:

    TOKEN = os.environ.get('TOKEN')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEFAULT_MAIL = os.environ.get('ADMIN')

    CERT_MAIL_PORT = int(os.environ.get('CERT_MAIL_PORT'))
    CERT_MAIL_SERVER = os.environ.get('CERT_MAIL_SERVER')
    CERT_MAIL_USERNAME = os.environ.get('CERT_MAIL_USERNAME')
    CERT_MAIL_PASSWORD = os.environ.get('CERT_MAIL_PASSWORD')
