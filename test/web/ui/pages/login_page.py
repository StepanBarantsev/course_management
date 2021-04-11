class LoginPage:

    def __init__(self, app):
        self.app = app

    def login(self, name, password):
        self.app.wd.find_element_by_css_selector("#username").send_keys(name)
        self.app.wd.find_element_by_css_selector("#password").send_keys(password)
        self.app.wd.find_element_by_css_selector("#submit").click()