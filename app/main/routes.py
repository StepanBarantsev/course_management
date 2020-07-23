from app.main import bp
from flask_login import login_required
from flask import render_template


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('main/index.html', title='Авторизация')
