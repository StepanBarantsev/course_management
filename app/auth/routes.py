from flask import render_template, redirect, url_for, flash
from flask_login import login_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))

        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))
    return render_template('auth/login.html', title='Sign In', form=form)
