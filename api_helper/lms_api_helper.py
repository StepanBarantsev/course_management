import api_helper.config
import requests


class LmsApiHelper:

    def __init__(self):
        self.lms_key = api_helper.config.ConfigApi.lms_key

    @staticmethod
    def get_student_by_lms_id(self, lms_id):
        requests.get(f'https://software-testing.ru/lms/webservice/rest/server.php?wstoken={self.lms_key}&wsfunction=core_user_get_users&criteria[0][key]=id&criteria[0][value]={lms_id}&moodlewsrestformat=json')
