import api_helper.config


class LmsApiHelper:

    def __init__(self):
        self.lms_key = api_helper.config.ConfigApi.lms_key

    def get_student_by_lms_id(self):
        pass
