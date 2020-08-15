from flask_login import login_required
from app.coursecreate import bp
from app.models import Course
from app.coursecreate.forms import CreateCourseProfileForm
from flask_login import current_user
from app import db
from flask import render_template, redirect, url_for, flash, request


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateCourseProfileForm(current_user)
    if form.validate_on_submit():
        new_course = Course(name=form.name.data, user_id=current_user.id)
        db.session.add(new_course)
        db.session.commit()
        flash('Новый курс был успешно создан!')
        return redirect(url_for('main.index'))
    return render_template('coursecreate/create.html', title='Создать курс', form=form)
