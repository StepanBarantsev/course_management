from app.main import bp
from flask_login import login_required, current_user
from flask import render_template, request, current_app, url_for


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    courses = current_user.get_all_not_deleted_courses().paginate(page, current_app.config['COURSES_PER_PAGE'], False)
    next_url = url_for('main.index', page=courses.next_num) if courses.has_next else None
    prev_url = url_for('main.index', page=courses.prev_num) if courses.has_prev else None
    return render_template('main/index.html', title='Курсы', courses=courses.items, next_url=next_url, prev_url=prev_url, current_page=page)
