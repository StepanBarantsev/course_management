from flask import Blueprint

bp = Blueprint('auth', __name__)

from web.app.auth import routes
