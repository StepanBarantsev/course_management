from flask import Blueprint

bp = Blueprint('main', __name__)

from web.app.main import routes

