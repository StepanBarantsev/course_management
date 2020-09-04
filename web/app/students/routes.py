from web.app.students import bp
from flask_login import login_required
from flask import render_template, request, flash, redirect, url_for
from web.app.models import Course, Student
from web.app import db
from web.app.students.forms import AddOrEditStudentForm
from api_helper.lms_api_helper import LmsApiHelper
import random


@bp.route('/', methods=['GET'])
@login_required
def index():
    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name
    students = course.get_all_not_delete_students()
    return render_template('students/index.html', title="Список студентов", course_name=course_name, students=students,
                           course_id=course_id)


@bp.route('/delete', methods=['POST'])
@login_required
def delete():
    return render_template('students/index.html')


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
                              freezed=False,
                              number_of_days=form.days.data,
                              lms_id=lms_id,
                              registration_code=generate_random_registration_code(),
                              telegram_id=None,
                              deleted=False,
                              course_id=course_id)

        db.session.add(new_student)
        db.session.commit()
        flash('Новый студент был успешно добавлен!')
        return redirect(url_for('students.index'))
    elif request.method == 'GET':
        form.days.data = course.default_num_days

    return render_template('students/addedit.html', title="Добавление студента", course_name=course_name, header="Добавление студента на курс ",
                           form=form)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name

    form = AddOrEditStudentForm(course, course_name, course.email)

    if form.validate_on_submit():
        pass
    elif request.method == 'GET':
        pass
    return render_template('students/edit.html', title="Редактировние информации о студенте", course_name=course_name,
                           header="Редактирование студента, обучающегося на курс ", form=form)


