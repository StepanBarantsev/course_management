class NavigationComponent:

    def __init__(self, app):
        self.app = app

    def check_edit_profile_link_present(self):
        self.app.check_element_present('a[href="/editprofile"]', 'Ссылка на редактирование профиля отсутстует на странице')
