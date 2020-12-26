from web.app.checks import bp
from flask_login import login_required
from flask import render_template, request
from web.app.models import Student
from web.app import db
from flask_login import current_user


@bp.route('/', methods=['GET'])
@login_required
def index():
    student_id = request.args.get('student_id', type=int)
    student = db.session.query(Student).filter(Student.id == student_id).first()

    if student.course.author.id == current_user.id:
        return render_template('checks/index.html', title=f"Список чеков студента {student.name}", student_name=student.name)
    else:
        return render_template('error/403.html', title='Ошибка доступа')
