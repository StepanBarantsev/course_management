from flask import Blueprint

bp = Blueprint('students', __name__)

from app.profile import routes