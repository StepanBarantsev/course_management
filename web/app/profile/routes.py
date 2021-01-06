from web.app.profile import bp
from flask_login import login_required
from web.app.profile.forms import EditProfileForm, ResetPasswordForm
from flask_login import current_user
from web.app import db
from flask import render_template, redirect, url_for, flash, request, current_app


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile/profile.html', title='Профиль', default_mail=current_app.config['ADMINS'][0])


@bp.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = EditProfileForm(current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        current_user.telegram_id = form.telegram_id.data
        current_user.lms_id = form.lms_id.data
        current_user.telegram_nickname = form.telegram_nickname.data
        current_user.flag_emails_from_default_mail = form.flag_emails_from_default_mail.data
        db.session.commit()
        flash('Изменения были успешно сохранены')
        return redirect(url_for('profile.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.lms_id.data = current_user.lms_id
        form.telegram_id.data = current_user.telegram_id
        form.telegram_nickname.data = current_user.telegram_nickname
        form.flag_emails_from_default_mail.data = current_user.flag_emails_from_default_mail
    return render_template('profile/edit.html', title='Редактирование профиля', form=form, default_mail=current_app.config['ADMINS'][0])


@bp.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm(current_user)
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Пароль был успешно изменен')
        return redirect(url_for('profile.profile'))
    return render_template('profile/reset_password.html', title='Изменение пароля', form=form)
