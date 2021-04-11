from selenium import webdriver


class Application:

    def __init__(self):
        self.wd = webdriver.Chrome()
