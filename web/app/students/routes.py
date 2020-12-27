from web.app.students import bp
from flask_login import login_required
from flask import render_template, request, flash, redirect, url_for, current_app
from web.app.models import Course, Student
from web.app import db
from web.app.students.forms import AddOrEditStudentForm
from api_helper.lms_api_helper import LmsApiHelper
import random
from flask_login import current_user
from sqlalchemy import update
from flask import jsonify


@bp.route('/', methods=['GET'])
@login_required
def index():
    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()

    student_filter = request.args.get('student_filter', 'active')
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort_type', "default")
    student_search = request.args.get('student_search', "")

    all_courses = current_user.get_all_not_deleted_courses()

    if student_filter == 'active':
        students = course.get_all_not_deleted_active_students()
    elif student_filter == 'freezed':
        students = course.get_all_not_deleted_freezed_students()
    elif student_filter == 'finished':
        students = course.get_all_not_deleted_finished_students()
    elif student_filter == 'dropped':
        students = course.get_all_not_deleted_dropped_students()
    elif student_filter == 'any':
        students = course.get_all_not_deleted_students()
    else:
        students = course.get_all_not_deleted_active_students()

    if student_search != "":
        students = course.find_students_by_search_param(students, student_search)

    if sort_type == 'name':
        students = students.order_by(Student.name)

    if sort_type == 'name_reversed':
        students = students.order_by(Student.name.desc())

    if sort_type == 'days':
        students = students.order_by(Student.number_of_days)

    if sort_type == 'days_reversed':
        students = students.order_by(Student.number_of_days.desc())


    students = students.paginate(page, current_app.config['ELEMENTS_PER_PAGE'], False)
    next_url = url_for('students.index', page=students.next_num, course_id=course_id, student_filter=student_filter) if students.has_next else None
    prev_url = url_for('students.index', page=students.prev_num, course_id=course_id, student_filter=student_filter) if students.has_prev else None

    if course.author.id == current_user.id:
        return render_template('students/index.html', title="Список студентов", course_name=course.name, students=students.items,
                               course_id=course_id, next_url=next_url, prev_url=prev_url, current_page=page,
                               student_filter=student_filter, all_courses=all_courses, sort_type=sort_type,
                               student_search=student_search, course_default_num_days=course.default_num_days)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/delete', methods=['POST'])
@login_required
def delete():
    course_id = int(request.form['course_id'])
    student_id = int(request.form['student_id'])
    student = db.session.query(Student).filter(Student.id == student_id).first()

    if student.course.author.id == current_user.id:
        Student.delete_student_by_id(student_id)
        db.session.commit()
        flash('Студент успешно удален!')
        return redirect(url_for('students.index', course_id=course_id))
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():

    def generate_random_registration_code():
        chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        code = ''
        for n in range(25):
            code += random.choice(chars)
        return code

    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name

    form = AddOrEditStudentForm(course)

    if form.validate_on_submit():
        lms_id = form.lms_id.data
        info_about_student_from_lms = LmsApiHelper.get_student_by_lms_id(lms_id)

        new_student = Student(name=info_about_student_from_lms['fullname'],
                              email=form.email.data,
                              lms_email=info_about_student_from_lms['email'],
                              number_of_days=form.days.data,
                              lms_id=lms_id,
                              registration_code=generate_random_registration_code(),
                              telegram_id=None,
                              deleted=False,
                              course_id=course_id,
                              status=Student.student_statuses["active"])

        db.session.add(new_student)
        db.session.commit()
        flash('Новый студент был успешно добавлен!')
        return redirect(url_for('students.index', course_id=course_id))
    elif request.method == 'GET':
        form.days.data = course.default_num_days

    return render_template('students/addedit.html', title="Добавление студента", course_name=course_name, header="Добавление студента на курс ",
                           form=form, for_edit=False)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    student_id = request.args.get('student_id', type=int)
    student = db.session.query(Student).filter(Student.id == student_id).first()

    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name

    if student.course.author.id == current_user.id:

        form = AddOrEditStudentForm(current_course=course, old_email=student.email, old_lms_id=student.lms_id)

        if form.validate_on_submit():
            if form.telegram_id_locked.data == "":
                telegram_id = None
            else:
                telegram_id = form.telegram_id_locked.data

            db.session.execute(update(Student).where(Student.id == student_id).values(
                              name=form.name_locked.data,
                              email=form.email.data,
                              lms_email=form.lms_email_locked.data,
                              number_of_days=form.days.data,
                              lms_id=form.lms_id.data,
                              registration_code=form.registration_code_locked.data,
                              telegram_id=telegram_id))
            db.session.commit()
            flash('Данные о студенте были успешно изменены!')
            return redirect(url_for('students.index', course_id=course_id))
        elif request.method == 'GET':
            form.name_locked.data = student.name
            form.email.data = student.email
            form.lms_email_locked.data = student.lms_email
            form.days.data = student.number_of_days
            form.lms_id.data = student.lms_id
            form.registration_code_locked.data = student.registration_code
            form.telegram_id_locked.data = student.telegram_id

        return render_template('students/addedit.html', title="Редактировние информации о студенте",
                               course_name=course_name, header="Редактирование студента, обучающегося на курсе ",
                               form=form, for_edit=True)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/freeze', methods=['POST'])
@login_required
def freeze():
    try:
        student_id = int(request.form['student_id'])
    except:
        flash('Что-то пошло не так. Подождите несколько секунд и попробуйте заморозить студента снова.')
        return {"error": True}
    Student.freeze_or_unfreeze_student_by_id(student_id)
    db.session.commit()
    return jsonify({"color": Student.query.filter_by(id=student_id).first().return_color_of_td(), "error": False})


@bp.route('/finish', methods=['POST'])
@login_required
def finish():
    try:
        student_id = int(request.form['student_id'])
    except:
        flash('Что-то пошло не так. Подождите несколько секунд и попробуйте завершить курс для студента снова.')
        return {"error": True}
    Student.finish_or_unfinish_student_by_id(student_id)
    db.session.commit()
    return jsonify({"color": Student.query.filter_by(id=student_id).first().return_color_of_td(), "error": False})


@bp.route('/drop', methods=['POST'])
@login_required
def drop():
    try:
        student_id = int(request.form['student_id'])
    except:
        flash('Что-то пошло не так. Подождите несколько секунд и попробуйте выполнить действие снова.')
        return {"error": True}
    Student.drop_or_undrop_student_by_id(student_id)
    db.session.commit()
    return jsonify({"color": Student.query.filter_by(id=student_id).first().return_color_of_td(), "error": False})


@bp.route('/add_days', methods=['POST'])
@login_required
def add_days():
    try:
        student_id = int(request.form['student_id'])
    except:
        flash('Что-то пошло не так. Подождите несколько секунд и попробуйте выполнить действие снова.')
        return {"error": True}
    number_of_days = Student.add_days_to_student(student_id)
    db.session.commit()
    return jsonify({"error": False, "num_days": number_of_days})


@bp.route('/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    try:
        course_id = request.args.get('course_id', type=int)
        q = request.args.get('q')
    except:
        flash('Что-то пошло не так. Подождите несколько секунд и попробуйте выполнить действие снова.')
        return {"error": True}

    course = Course.get_course_by_id(course_id)
    students = course.get_all_not_deleted_students()

    lst = [student.lms_email for student in students if student.lms_email.startswith(q)] + \
          [student.email for student in students if student.email.startswith(q)] + \
          [student.name for student in students if student.name.startswith(q)] + \
          [str(student.telegram_id) for student in students if (student.telegram_id is not None and str(student.telegram_id).startswith(q))]

    return jsonify(lst)
