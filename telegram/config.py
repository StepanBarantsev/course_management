import os


class ConfigTelegram:

    TOKEN = os.environ.get('TOKEN')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEFAULT_MAIL = os.environ.get('ADMIN')
