from app.main import bp
from flask_login import login_required


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    return 'Привет мир!'