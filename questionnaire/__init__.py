from flask import Blueprint

questionnaire_bp = Blueprint('questionnaire', __name__, url_prefix='/questionnaire')

from . import routes