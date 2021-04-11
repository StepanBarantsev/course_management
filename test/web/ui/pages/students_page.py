from web.app.models import Student
from time import sleep


class StudentsPage:

    def __init__(self, app):
        self.app = app

    def get_student_status(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        td = row.find_elements_by_css_selector('td')[0]
        color = td.get_attribute('bgcolor')

        if str(color) == '98ff98':
            return Student.student_statuses['active']
        if str(color) == '9966cc':
            return Student.student_statuses['finished']
        if str(color) == 'aqua':
            return Student.student_statuses['freezed']
        if str(color) == 'gray':
            return Student.student_statuses['dropped']

    def change_status_to_freezed(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        row.find_element_by_css_selector('[title="Заморозить"]').click()

    def change_status_to_dropped(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        row.find_element_by_css_selector('[title="Бросил курс"]').click()

    def change_status_to_finished(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        row.find_element_by_css_selector('[title="Завершил курс"]').click()

    def add_days_to_student(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        row.find_element_by_css_selector('[name="add_days"]').click()

    def get_student_number_of_days(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        td = row.find_elements_by_css_selector('td')[3]
        number = int(td.text)
        return number

    def find_student(self, text):
        self.app.wd.find_element_by_css_selector('.basicAutoComplete').send_keys(text)
        self.app.wd.find_element_by_css_selector('#search_student').click()

    def get_number_of_students_on_page(self):
        # Тут -1, потому что есть строка заголовков
        return len(self.app.wd.find_elements_by_css_selector('.table-responsive tr')) - 1

    def get_student_name(self, student_index):
        row = self.app.wd.find_elements_by_css_selector('.table-responsive tr')[student_index + 1]
        td = row.find_elements_by_css_selector('td')[0]
        return td.text

    def filter_by_status_freezed(self):
        self.app.wd.find_elements_by_css_selector('#block_filters .form-control')[1].click()
        sleep(1)
        self.app.wd.find_element_by_css_selector('#block_filters .form-control [value="freezed"]').click()

