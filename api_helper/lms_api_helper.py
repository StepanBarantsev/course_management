import api_helper.config
import requests
import json


class LmsApiHelper:

    lms_key = api_helper.config.ConfigApi.lms_key

    @staticmethod
    def get_student_by_lms_id(lms_id):
        return json.loads(requests.get(f'https://software-testing.ru/lms/webservice/rest/server.php?wstoken={LmsApiHelper.lms_key}&wsfunction=core_user_get_users&criteria[0][key]=id&criteria[0][value]={lms_id}&moodlewsrestformat=json').text)

