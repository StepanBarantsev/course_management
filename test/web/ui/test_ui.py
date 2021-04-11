from time import sleep
from test.db_helper import create_course


def test_edit_profile_data(session, app, user_logined_minimal):
    app.courses_page.check_course_table_not_present()
    app.navigation_component.check_edit_profile_link_present()


def test_go_by_pages(session, app, user_logined):
    for i in range(11):
        create_course(session, user_id=user_logined.id, course_name=f'Название {i}', course_lms_id=i)

    app.refresh()

    num_of_rows_on_first_page = app.courses_page.get_num_of_courses_on_page()
    assert num_of_rows_on_first_page == 10

    app.courses_page.go_to_next_page()
    num_of_rows_on_second_page = app.courses_page.get_num_of_courses_on_page()
    assert num_of_rows_on_second_page == 1
