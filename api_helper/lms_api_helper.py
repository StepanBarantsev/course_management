import api_helper.config
import requests
import json


class LmsApiHelper:

    lms_key = api_helper.config.ConfigApi.lms_key
    # Мой id, так как для некоторых запросов нужен id студента. В целом подойдет любой, вот указываю мой
    config_student_id = 10622

    @staticmethod
    def get_student_by_lms_id(lms_id):
        return json.loads(requests.get(f'https://software-testing.ru/lms/webservice/rest/server.php?wstoken={LmsApiHelper.lms_key}&wsfunction=core_user_get_users&criteria[0][key]=id&criteria[0][value]={lms_id}&moodlewsrestformat=json', headers={"User-Agent": "Mozilla/5.0"}).text)['users'][0]

    @staticmethod
    def is_task_completed(student_lms_id, task_number, course_id, gradepass=5):
        task_info = LmsApiHelper.get_task_by_number(task_number, student_lms_id, course_id)
        return task_info['grades'][0]['grade'] == gradepass

    # Соглашение -- названия заданий должны быть в формате "Задание 1.1"
    # Либо "1.1 Установка Selenium IDE"
    # В общем, нужно чтобы в названии присутствовали две цифры, разделенные точкой и больше не было цифр.
    # Все остальные символы должны быть буквенными
    # Первая цифра -- номер занятия
    # Вторая цифра -- номер задания в занятии
    @staticmethod
    def get_task_by_number(task_number, student_lms_id, course_id):
        task_number = str(task_number)
        lst = LmsApiHelper.get_all_tasks_for_student(student_lms_id, course_id)
        for element in lst:
            tmp_number = LmsApiHelper.delete_symbols_except_dots_and_digits(element['name'])
            if tmp_number == task_number:
                return element

    @staticmethod
    def get_task_by_fullname(fullname, student_lms_id, course_id):
        lst = LmsApiHelper.get_all_tasks_for_student(student_lms_id, course_id)
        for element in lst:
            if element['name'] == fullname:
                return element

    @staticmethod
    def get_task_by_id(lms_id, student_lms_id, course_id):
        lst = LmsApiHelper.get_all_tasks_for_student(student_lms_id, course_id)
        for element in lst:
            if element['activityid'] == str(lms_id):
                return element

    @staticmethod
    def delete_symbols_except_dots_and_digits(string):
        return ''.join([i for i in string if i == '.' or i.isdigit()])

    @staticmethod
    def get_all_tasks_for_student(student_lms_id, course_id):
        request = f'https://software-testing.ru/lms/webservice/rest/server.php?wstoken={LmsApiHelper.lms_key}&wsfunction=core_grades_get_grades&courseid={course_id}&userids[0]={student_lms_id}&moodlewsrestformat=json'
        result = requests.get(request, headers={"User-Agent": "Mozilla/5.0"})
        return result.json()['items'][1:]

    @staticmethod
    def can_we_give_certificate_to_student(student_lms_id, course_id):
        try:
            tasks = LmsApiHelper.get_all_tasks_for_student(student_lms_id, course_id)
        except KeyError:
            return False
        for task in tasks:
            # По соглашению считаем что задание с gradepass == 0 является необязательным
            if task['gradepass'] != 0:
                if task['grades'][0]['grade'] is None:
                    return False
                if task['grades'][0]['grade'] < task['gradepass']:
                    return False
        return True
