from web.app.students import bp
from flask_login import login_required
from flask import render_template, request, flash, redirect, url_for
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

    if course.author.id == current_user.id:
        course_name = course.name
        students = course.get_all_not_delete_students()
        return render_template('students/index.html', title="Список студентов", course_name=course_name, students=students,
                               course_id=course_id)
    else:
        return render_template('error/403.html', title='Ошибка доступа')


@bp.route('/delete', methods=['POST'])
@login_required
def delete():
    course_id = int(request.form['course_id'])
    student_id = int(request.form['student_id'])
    Student.delete_student_by_id(student_id)
    db.session.commit()
    flash('Студент успешно удален!')
    return redirect(url_for('students.index', course_id=course_id))


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
    return jsonify({"color": Student.query.filter_by(id=student_id).first().return_color_of_td(),
                    "error": False})
