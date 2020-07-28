from flask import Blueprint

bp = Blueprint('coursecreate', __name__)

from app.coursecreate import routes