from flask import Blueprint

bp = Blueprint('students', __name__)

from web.app.students import routes