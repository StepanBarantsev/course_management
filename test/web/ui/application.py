from selenium import webdriver
import os
from test.web.ui.pages.login_page import LoginPage
from test.web.ui.pages.courses_page import CoursesPage
from test.web.ui.pages.students_page import StudentsPage
from test.web.ui.components.navigation_component import NavigationComponent


class Application:

    def __init__(self):
        self.wd = webdriver.Chrome()
        self.wd.implicitly_wait(10)
        self.url = os.getenv('BASE_URL')

        self.login_page = LoginPage(self)
        self.courses_page = CoursesPage(self)
        self.students_page = StudentsPage(self)

        self.navigation_component = NavigationComponent(self)

    def open_base_page(self):
        self.wd.get(self.url)

    def check_element_present(self, locator, error_text=None):
        if error_text is None:
            error_text = f'Элемент с локатором {locator} не найден'

        try:
            self.wd.find_element_by_css_selector(locator)
        except:
            raise AssertionError(error_text)

    def check_element_not_present(self, locator, error_text=None):
        if error_text is None:
            error_text = f'Элемент с локатором {locator} найден'

        try:
            self.wd.implicitly_wait(0)
            self.wd.find_element_by_css_selector(locator)
            raise AssertionError(error_text)
        except:
            pass
        finally:
            self.wd.implicitly_wait(10)

    def refresh(self):
        self.wd.refresh()
