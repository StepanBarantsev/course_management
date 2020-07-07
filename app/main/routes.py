from app.main import bp


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return 'Привет мир!'
