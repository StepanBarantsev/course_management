class CoursesPage:

    def __init__(self, app):
        self.app = app

    def check_course_table_present(self):
        self.app.check_element_present('.table-responsive', 'Таблица с курсами не найдена')

    def check_course_table_not_present(self):
        self.app.check_element_not_present('.table-responsive', 'Таблица с курсами найдена')

    def get_num_of_courses_on_page(self):
        # Тут -1, потому что есть строка заголовков
        return len(self.app.wd.find_elements_by_css_selector('.table-responsive tr')) - 1

    def go_to_next_page(self):
        self.app.wd.find_elements_by_css_selector('.page-link')[1].click()

    def go_to_students_of_course_by_course_number(self, course_number):
        self.app.wd.find_elements_by_css_selector('a[title="Студенты"]')[course_number].click()

