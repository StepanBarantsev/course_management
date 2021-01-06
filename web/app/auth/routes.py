from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_user, current_user, logout_user
from web.app import db
from web.app.auth import bp
from web.app.auth.forms import LoginForm, RegistrationForm
from web.app.models import User
from web.app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from web.app.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.index'))

        flash("Неправильное имя пользователя/пароль", 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', title='Авторизация', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # По идее отсекать это на этапе валидации полей низя, потому что ее (валидацию) можно отключить
        if form.registration_code.data == current_app.config['CODE_FOR_REGISTRATION']:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно')
            return redirect(url_for('auth.login'))
        else:
            return render_template('error/403.html', title='Неверный код регистрации')
    return render_template('auth/register.html', title='Регистрация', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('На Вашу почту была отправлена инструкция для смены пароля')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Смена пароля', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль был успешно изменен')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

