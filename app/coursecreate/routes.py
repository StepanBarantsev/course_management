from flask_login import login_required
from app.coursecreate import bp
from app.models import Course
from app.coursecreate.forms import CreateOrEditCourseForm
from flask_login import current_user
from app import db
from flask import render_template, redirect, url_for, flash, request
from sqlalchemy import update


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():

    form = CreateOrEditCourseForm(current_user)

    if request.method == 'GET':

        if current_user.telegram_id is not None:
            form.trainer_telegram_id.data = current_user.telegram_id

        if current_user.lms_id is not None:
            form.trainer_lms_id.data = current_user.lms_id

        return render_template('coursecreate/editcreate.html', title='Создать курс', form=form, from_post=False)

    if request.method == 'POST':

        if form.validate_on_submit():
            new_course = Course(name=form.name.data, user_id=current_user.id, lms_id=form.lms_id.data,
                                trainer_lms_id=form.trainer_lms_id.data,
                                trainer_telegram_id=form.trainer_telegram_id.data)

            db.session.add(new_course)
            db.session.commit()
            flash('Новый курс был успешно создан!')
            return redirect(url_for('main.index'))

        return render_template('coursecreate/editcreate.html', title='Создать курс', form=form, from_post=True)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    course_id = request.args.get('course_id', 1, type=int)
    course = db.session.query(Course).filter(Course.id == course_id).first()
    form = CreateOrEditCourseForm(current_user, course.name, course.lms_id)
    if form.validate_on_submit():
        db.session.execute(update(Course).where(Course.id == course_id).values(name=form.name.data, lms_id=form.lms_id.data,
                                                                               trainer_lms_id=form.trainer_lms_id.data,
                                                                               trainer_telegram_id=form.trainer_telegram_id.data))
        db.session.commit()
        flash('Данные курса были успешно изменены!')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.name.data = course.name
        form.lms_id.data = course.lms_id
        form.trainer_lms_id.data = course.trainer_lms_id
        form.trainer_telegram_id.data = course.trainer_telegram_id

    return render_template('coursecreate/editcreate.html', title='Редактировать курс', form=form)


@bp.route('/delete', methods=['POST'])
@login_required
def delete():
    course_id = int(request.form['course_id'])
    Course.delete_course_by_id(course_id)
    db.session.commit()
    flash('Курс успешно удален!')
    return redirect(url_for('main.index'))

