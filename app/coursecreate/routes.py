from flask_login import login_required
from flask import render_template
from app.coursecreate import bp


@bp.route('/create', methods=['GET'])
@login_required
def create():
    return render_template('coursecreate/create.html', title='Создать курс')
