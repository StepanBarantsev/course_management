from selenium import webdriver
import os
from test.web.ui.pages.login_page import LoginPage


class Application:

    def __init__(self):
        self.wd = webdriver.Chrome()
        self.url = os.getenv('BASE_URL')

        self.login_page = LoginPage(self)

    def open_base_page(self):
        self.wd.get(self.url)
