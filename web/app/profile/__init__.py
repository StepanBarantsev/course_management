from flask import Blueprint

bp = Blueprint('profile', __name__)

from web.app.profile import routes