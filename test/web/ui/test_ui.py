from time import sleep
from test.db_helper import create_course, create_student
from web.app.models import Student


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


def test_change_student_status(session, app, user_logined):

    course = create_course(session, user_id=user_logined.id, course_name=f'Название курса', course_lms_id=1)
    create_student(session, course_id=course.id, student_name=f'Имя студента', student_lms_id=1)

    app.refresh()

    app.courses_page.go_to_students_of_course_by_course_number(0)
    status = app.students_page.get_student_status(0)

    assert status == Student.student_statuses['active']

    app.students_page.change_status_to_dropped(0)
    sleep(1)
    status = app.students_page.get_student_status(0)

    assert status == Student.student_statuses['dropped']

    app.students_page.change_status_to_freezed(0)
    sleep(1)
    status = app.students_page.get_student_status(0)

    assert status == Student.student_statuses['freezed']

    app.students_page.change_status_to_finished(0)
    sleep(1)
    status = app.students_page.get_student_status(0)

    assert status == Student.student_statuses['finished']


def test_add_days_to_student(session, app, user_logined):

    course = create_course(session, user_id=user_logined.id, course_name=f'Название курса', course_lms_id=1)
    create_student(session, course_id=course.id, student_name=f'Имя студента', student_lms_id=1)

    app.refresh()

    app.courses_page.go_to_students_of_course_by_course_number(0)
    days = app.students_page.get_student_number_of_days(0)

    assert days == 0

    app.students_page.add_days_to_student(0)
    sleep(1)
    days = app.students_page.get_student_number_of_days(0)

    assert days == 30


def test_find_student(session, app, user_logined):
    course = create_course(session, user_id=user_logined.id, course_name=f'Название курса', course_lms_id=1)
    create_student(session, course_id=course.id, student_name=f'Студент Студентович', student_lms_id=1)
    create_student(session, course_id=course.id, student_name=f'Школьник Школьникович', student_lms_id=2)

    app.refresh()

    app.courses_page.go_to_students_of_course_by_course_number(0)
    number_of_students = app.students_page.get_number_of_students_on_page()

    assert number_of_students == 2

    app.students_page.find_student('Школьник Школьникович')
    sleep(1)
    number_of_students = app.students_page.get_number_of_students_on_page()
    first_student_name = app.students_page.get_student_name(0)

    assert number_of_students == 1
    assert first_student_name == 'Школьник Школьникович'


def test_filter_students_by_status(session, app, user_logined):
    course = create_course(session, user_id=user_logined.id, course_name=f'Название курса', course_lms_id=1)
    create_student(session, course_id=course.id, student_name=f'Студент Студентович', student_lms_id=1)
    create_student(session, course_id=course.id, student_name=f'Школьник Школьникович', student_lms_id=2)

    app.refresh()

    app.courses_page.go_to_students_of_course_by_course_number(0)
    app.students_page.change_status_to_freezed(0)
    number_of_students = app.students_page.get_number_of_students_on_page()

    assert number_of_students == 2

    app.students_page.filter_by_status_freezed()
    number_of_students = app.students_page.get_number_of_students_on_page()
    first_student_name = app.students_page.get_student_name(0)
    status = app.students_page.get_student_status(0)

    assert number_of_students == 1
    assert first_student_name == 'Студент Студентович'
    assert status == Student.student_statuses['freezed']
