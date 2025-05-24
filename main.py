from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, jwt, mail, migrate
from flask_migrate import upgrade
from models import User
from flasgger import Swagger
from admin import register_admin

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    CORS(app)

    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Project API",
            "description": "Flask + Swagger + JWT 認證文件",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "請輸入 JWT：Bearer <你的 token>"
            }
        }
    })

    from auth import auth_bp
    app.register_blueprint(auth_bp)
    from users import users_bp
    app.register_blueprint(users_bp)
    from questionnaire import questionnaire_bp
    app.register_blueprint(questionnaire_bp)

    register_admin(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
