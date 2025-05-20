from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import routes  # 匯入 routes 來綁定 blueprint