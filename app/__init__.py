from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Войдите в систему, чтобы просматривать данную страницу!'
bootstrap = Bootstrap()
moment = Moment()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.coursecreate import bp as coursecreate_bp
    app.register_blueprint(coursecreate_bp, url_prefix='/coursecreate')

    from app.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from app.students import bp as students_bp
    app.register_blueprint(students_bp)

    return app


from app import models