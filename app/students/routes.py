from app.students import bp
from flask_login import login_required, current_user
from flask import render_template, request, current_app, url_for
from app.models import Course
from app import db
from app.students.forms import AddOrEditStudentForm


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
    form = AddOrEditStudentForm()
    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name
    return render_template('students/addedit.html', title="Добавление студента", course_name=course_name, header="Добавление студента на курс ",
                           form=form)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = AddOrEditStudentForm()
    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name
    return render_template('students/edit.html', title="Редактировние информации о студенте", course_name=course_name,
                           header="Редактирование студента, обучающегося на курс ", form=form)
