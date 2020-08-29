from flask import Blueprint

bp = Blueprint('coursecreate', __name__)

from web.app.coursecreate import routes