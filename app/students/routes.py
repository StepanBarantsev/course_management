from app.students import bp
from flask_login import login_required, current_user
from flask import render_template, request, current_app, url_for
from app.models import Course
from app import db


@bp.route('/', methods=['GET'])
@login_required
def index():
    course_id = request.args.get('course_id', type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    course_name = course.name
    students = course.students
    return render_template('students/index.html', title="Список студентов", course_name=course_name, students=students)


@bp.route('/delete', methods=['POST'])
@login_required
def delete():
    return render_template('students/index.html', title="Список студентов", course_name=course_name, students=students)
