from flask import Blueprint


api = Blueprint('api', __name__, url_prefix='/api')

auth_api = Blueprint('auth_api', __name__, url_prefix='/auth')

api.register_blueprint(auth_api)