import os


class ConfigApi:
    lms_key = os.environ.get('LMS_KEY')
    fauna_key = os.environ.get('FAUNA_KEY')
