from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # 原本是 password
    name = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_filled = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('密碼不能直接存取')

    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)
    
class MoodLog(db.Model):
    __tablename__ = 'mood_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    mood = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref=db.backref('mood_logs', lazy=True))