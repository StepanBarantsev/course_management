from app.profile import bp
from flask_login import login_required
from app.profile.forms import EditProfileForm
from flask_login import current_user
from app import db
from flask import render_template, redirect, url_for, flash, request


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile/profile.html', title='Профиль')


@bp.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = EditProfileForm(current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        db.session.commit()
        flash('Изменения были успешно сохранены')
        return redirect(url_for('profile.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
    return render_template('profile/edit.html', title='Редактирование профиля', form=form)
