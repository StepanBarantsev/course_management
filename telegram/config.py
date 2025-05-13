import os


class ConfigTelegram:

    TOKEN = os.environ.get('TOKEN')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    DEFAULT_MAIL = os.environ.get('ADMIN')

    MAIL_ADDRESS = os.getenv("MAIL_ADDRESS")
    MAIL_KEY = os.getenv("MAIL_KEY")
    CERT_MAIL_ADDR = os.getenv("CERT_MAIL_ADDR")

    COUPON_CODE = os.environ.get('COUPON_CODE')

    CERT_DB_HOST = os.getenv("CERT_DB_HOST")
    CERT_DB_PORT = os.getenv("CERT_DB_PORT")
    CERT_DB_NAME = os.getenv("CERT_DB_NAME")
    CERT_DB_USER = os.getenv("CERT_DB_USER")
    CERT_DB_PASSWORD = os.getenv("CERT_DB_PASSWORD")
