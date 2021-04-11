from web.app.models import Student


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
