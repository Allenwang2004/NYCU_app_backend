from flask_admin import Admin
from admin.views import ProtectedModelView, MoodLogView
from admin.routes import bp as admin_auth_bp
from models import User, MoodLog
from extensions import db

def register_admin(app):
    # 註冊登入 Blueprint
    app.register_blueprint(admin_auth_bp)

    # 註冊 Flask-Admin
    admin = Admin(app, name="資料庫後台管理", template_mode="bootstrap4")
    admin.add_view(ProtectedModelView(User, db.session))
    admin.add_view(MoodLogView(MoodLog, db.session))