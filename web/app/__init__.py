from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from web.config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Войдите в систему, чтобы просматривать данную страницу!'
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_error_handler(404, page_not_found)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    from web.app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from web.app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from web.app.coursecreate import bp as coursecreate_bp
    app.register_blueprint(coursecreate_bp, url_prefix='/coursecreate')

    from web.app.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from web.app.students import bp as students_bp
    app.register_blueprint(students_bp, url_prefix='/students')

    from web.app.checks import bp as checks_bp
    app.register_blueprint(checks_bp, url_prefix='/checks')

    return app


def page_not_found(e):
    return render_template('error/404.html'), 404
