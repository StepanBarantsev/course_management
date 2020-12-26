from flask import Blueprint

bp = Blueprint('checks', __name__)

from web.app.checks import routes